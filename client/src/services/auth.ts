
import { api } from './api';
import { notificationService } from './notification';
import { captchaService } from './captcha';

export interface PhoneValidationResponse {
  isValid: boolean;
  isVoip: boolean;
  carrier?: string;
  region?: string;
}

export interface OTPResponse {
  success: boolean;
  expiresAt: string;
  attempts: number;
  requiresCaptcha: boolean;
}

export interface VerificationResult {
  success: boolean;
  token?: string;
  error?: string;
}

export interface DeviceInfo {
  type: string;
  browser: string;
  os: string;
  ip?: string;
}

export interface AuditLog {
  eventType: string;
  userId?: string;
  phoneNumber?: string;
  deviceInfo: DeviceInfo;
  timestamp: string;
  status: 'success' | 'failure';
  details?: string;
}

class AuthService {
  private failedAttempts: Map<string, number> = new Map();
  private MAX_ATTEMPTS = 5;
  private LOCKOUT_TIME = 15 * 60 * 1000; // 15 minutes
  private lockedAccounts: Map<string, number> = new Map();
  
  private getDeviceInfo(): DeviceInfo {
    return {
      type: 'web',
      browser: navigator.userAgent,
      os: navigator.platform
    };
  }

  private async logAuditEvent(event: Partial<AuditLog>): Promise<void> {
    const auditLog: AuditLog = {
      eventType: event.eventType || 'unknown',
      userId: event.userId,
      phoneNumber: event.phoneNumber,
      deviceInfo: event.deviceInfo || this.getDeviceInfo(),
      timestamp: new Date().toISOString(),
      status: event.status || 'success',
      details: event.details
    };
    
    console.log('AUDIT LOG:', auditLog);
    
    // In real implementation, send to backend
    try {
      await api.post('/audit/log', auditLog);
    } catch (error) {
      // Even if the API call fails, we've logged it locally
      console.error('Failed to send audit log:', error);
    }
  }

  private isAccountLocked(phone: string): boolean {
    const lockTime = this.lockedAccounts.get(phone);
    if (lockTime && Date.now() < lockTime) {
      return true;
    } else if (lockTime) {
      // Lockout period expired
      this.lockedAccounts.delete(phone);
      this.failedAttempts.delete(phone);
    }
    return false;
  }

  async validatePhone(phone: string): Promise<PhoneValidationResponse> {
    try {
      await this.logAuditEvent({
        eventType: 'phone_validation_attempt',
        phoneNumber: phone,
        status: 'success'
      });
      
      const response = await api.post<PhoneValidationResponse>('/auth/validate-phone', {
        phone,
        device: this.getDeviceInfo()
      });
      
      // Mock response for MVP
      return {
        isValid: true,
        isVoip: false,
        carrier: 'Mock Carrier',
        region: 'US'
      };
    } catch (error) {
      await this.logAuditEvent({
        eventType: 'phone_validation_attempt',
        phoneNumber: phone,
        status: 'failure',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  async requestOTP(phone: string, isLogin: boolean = false): Promise<OTPResponse> {
    try {
      if (this.isAccountLocked(phone)) {
        const remainingTime = Math.ceil(
          (this.lockedAccounts.get(phone)! - Date.now()) / 60000
        );
        
        await this.logAuditEvent({
          eventType: 'otp_request_blocked',
          phoneNumber: phone,
          status: 'failure',
          details: `Account locked for ${remainingTime} more minutes`
        });
        
        return {
          success: false,
          expiresAt: new Date().toISOString(),
          attempts: this.failedAttempts.get(phone) || 0,
          requiresCaptcha: true
        };
      }
      
      const attempts = this.failedAttempts.get(phone) || 0;
      const requiresCaptcha = await captchaService.shouldShowCaptcha(
        undefined, undefined, attempts
      );
      
      await this.logAuditEvent({
        eventType: isLogin ? 'login_otp_request' : 'registration_otp_request',
        phoneNumber: phone,
        status: 'success'
      });
      
      const response = await api.post<OTPResponse>('/auth/request-otp', {
        phone,
        purpose: isLogin ? 'login' : 'registration',
        device: this.getDeviceInfo()
      });
      
      // Mock response for MVP
      return {
        success: true,
        expiresAt: new Date(Date.now() + 5 * 60000).toISOString(), // 5 minutes
        attempts,
        requiresCaptcha
      };
    } catch (error) {
      await this.logAuditEvent({
        eventType: isLogin ? 'login_otp_request' : 'registration_otp_request',
        phoneNumber: phone,
        status: 'failure',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  async verifyOTP(phone: string, otp: string): Promise<VerificationResult> {
    try {
      if (this.isAccountLocked(phone)) {
        const remainingTime = Math.ceil(
          (this.lockedAccounts.get(phone)! - Date.now()) / 60000
        );
        
        await this.logAuditEvent({
          eventType: 'otp_verification_blocked',
          phoneNumber: phone,
          status: 'failure',
          details: `Account locked for ${remainingTime} more minutes`
        });
        
        return { 
          success: false, 
          error: `Account locked. Try again in ${remainingTime} minutes.`
        };
      }
      
      const response = await api.post<VerificationResult>('/auth/verify-otp', {
        phone,
        otp,
        device: this.getDeviceInfo()
      });
      
      // Mock successful verification
      if (otp === '123456') {
        const token = 'mock_jwt_token_' + Date.now();
        localStorage.setItem('pvtelv_auth', 'true');
        localStorage.setItem('pvtelv_token', token);
        
        // Reset failed attempts
        this.failedAttempts.delete(phone);
        
        await this.logAuditEvent({
          eventType: 'otp_verification_success',
          phoneNumber: phone,
          status: 'success'
        });
        
        // Send welcome notification for new users
        const isNewUser = !localStorage.getItem('pvtelv_welcomed');
        if (isNewUser) {
          localStorage.setItem('pvtelv_welcomed', 'true');
          await notificationService.sendWelcomeNotification('user123', phone);
        }
        
        return { success: true, token };
      }
      
      // Handle failed attempt
      const attempts = (this.failedAttempts.get(phone) || 0) + 1;
      this.failedAttempts.set(phone, attempts);
      
      await this.logAuditEvent({
        eventType: 'otp_verification_failure',
        phoneNumber: phone,
        status: 'failure',
        details: `Failed attempt ${attempts} of ${this.MAX_ATTEMPTS}`
      });
      
      // Check if account should be locked
      if (attempts >= this.MAX_ATTEMPTS) {
        const lockUntil = Date.now() + this.LOCKOUT_TIME;
        this.lockedAccounts.set(phone, lockUntil);
        
        await this.logAuditEvent({
          eventType: 'account_locked',
          phoneNumber: phone,
          status: 'failure',
          details: `Account locked until ${new Date(lockUntil).toISOString()}`
        });
        
        return { 
          success: false, 
          error: `Too many failed attempts. Account locked for 15 minutes.`
        };
      }
      
      return { 
        success: false, 
        error: `Invalid OTP. ${this.MAX_ATTEMPTS - attempts} attempts remaining.`
      };
    } catch (error) {
      await this.logAuditEvent({
        eventType: 'otp_verification_error',
        phoneNumber: phone,
        status: 'failure',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  async logout(sessionId?: string): Promise<boolean> {
    try {
      await this.logAuditEvent({
        eventType: 'logout',
        userId: 'user123', // In a real app, get from token
        status: 'success'
      });
      
      if (sessionId) {
        // Revoke specific session
        await api.post('/auth/revoke-session', { sessionId });
      } else {
        // Revoke current session
        localStorage.removeItem('pvtelv_auth');
        localStorage.removeItem('pvtelv_token');
      }
      return true;
    } catch (error) {
      await this.logAuditEvent({
        eventType: 'logout_error',
        userId: 'user123', // In a real app, get from token
        status: 'failure',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  async revokeAllOtherSessions(): Promise<boolean> {
    try {
      await api.post('/auth/revoke-all-sessions', {
        exceptCurrent: true
      });
      
      await this.logAuditEvent({
        eventType: 'revoke_all_sessions',
        userId: 'user123', // In a real app, get from token
        status: 'success'
      });
      
      return true;
    } catch (error) {
      await this.logAuditEvent({
        eventType: 'revoke_all_sessions_error',
        userId: 'user123', // In a real app, get from token
        status: 'failure',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
      
      throw error;
    }
  }

  // Helper to check if user is authenticated
  isAuthenticated(): boolean {
    return localStorage.getItem('pvtelv_auth') === 'true';
  }

  // Get current auth token
  getToken(): string | null {
    return localStorage.getItem('pvtelv_token');
  }
}

export const authService = new AuthService();
