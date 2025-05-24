import { api, ApiResponse } from './api'; // Ensure ApiResponse is imported if used in return types directly
import { notificationService } from './notification';
// import { captchaService } from './captcha'; // captchaService is removed as per plan

export interface PhoneValidationResponse {
  isValid: boolean;
  isVoip?: boolean; // Optional as per typical API responses
  carrier?: string;
  region?: string;
  error?: string; // Added for error propagation
}

export interface OTPResponse {
  success: boolean;
  message?: string; // Backend might send a message
  expiresAt?: string; // Optional if not always present
  attemptsRemaining?: number; // Backend might send this
  lockoutUntil?: string; // Backend might send this
  requiresCaptcha?: boolean; // Backend might send this
  error?: string; // Added for error propagation
}

export interface VerificationResult {
  success: boolean;
  token?: string;
  error?: string;
  userId?: string; // Optionally, backend might return userId
}

export interface DeviceInfo {
  type: string;
  browser: string;
  os: string;
  ip?: string; // Usually captured backend-side, but client can provide some
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
  // Client-side state for attempts/lockout REMOVED
  // private failedAttempts: Map<string, number> = new Map();
  // private MAX_ATTEMPTS = 5;
  // private LOCKOUT_TIME = 15 * 60 * 1000; // 15 minutes
  // private lockedAccounts: Map<string, number> = new Map();

  private getDeviceInfo(): DeviceInfo {
    // This is basic. More sophisticated fingerprinting can be done.
    return {
      type: 'web', // Could be 'mobile_web', 'desktop_web'
      browser: navigator.userAgent, // General user agent string
      os: navigator.platform,       // OS platform
      // IP is best determined server-side, but some client-side info can be gathered.
    };
  }

  private async logAuditEvent(event: Partial<AuditLog>): Promise<void> {
    const auditLog: AuditLog = {
      eventType: event.eventType || 'unknown',
      userId: event.userId, // TODO: Populate with actual user ID from token/state post-login
      phoneNumber: event.phoneNumber,
      deviceInfo: event.deviceInfo || this.getDeviceInfo(),
      timestamp: new Date().toISOString(),
      status: event.status || 'success',
      details: event.details,
    };

    console.log('AUDIT LOG:', auditLog); // Keep client-side log for debugging

    try {
      // Fire-and-forget for audit logs is often acceptable, but handle errors if crucial
      await api.post('/audit/log', auditLog);
    } catch (error) {
      console.error('Failed to send audit log:', error);
    }
  }

  // isAccountLocked method REMOVED

  async validatePhone(phone: string): Promise<PhoneValidationResponse> {
    try {
      await this.logAuditEvent({
        eventType: 'phone_validation_attempt',
        phoneNumber: phone,
        status: 'success', // Log attempt, backend determines actual success
      });

      const response = await api.post<PhoneValidationResponse>('/auth/validate-phone', {
        phone,
        device: this.getDeviceInfo(),
      });

      if (response.data) {
        return response.data; // Assumes backend returns PhoneValidationResponse structure
      } else {
        // Error from api.ts or unexpected structure
        await this.logAuditEvent({
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: response.error || 'API error or invalid response structure',
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        // Error from api.ts or unexpected structure
        const errorDetail = response.error || 'API error or invalid response structure for validatePhone';
        console.error(`AuthService.validatePhone Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'phone_validation_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        return { 
          isValid: false, 
          error: response.error || 'Phone validation failed due to API error.' 
        };
      }
    } catch (error) { // Catch errors from api.post itself (e.g. network)
      const errorMessage = error instanceof Error ? error.message : 'Unknown error during phone validation.';
      await this.logAuditEvent({
        eventType: 'phone_validation_failure',
        phoneNumber: phone,
        status: 'failure',
        details: errorMessage,
      });
      return { isValid: false, error: errorMessage };
    }
  }

  async requestOTP(phone: string, isLogin: boolean = false): Promise<OTPResponse> {
    // Client-side lockout logic REMOVED
    // Client-side CAPTCHA trigger logic REMOVED
    
    const eventType = isLogin ? 'login_otp_request' : 'registration_otp_request';
    try {
      await this.logAuditEvent({
        eventType: eventType,
        phoneNumber: phone,
        status: 'success', // Log attempt
      });

      const response = await api.post<OTPResponse>('/auth/request-otp', {
        phone,
        purpose: isLogin ? 'login' : 'registration',
        device: this.getDeviceInfo(),
      });

      if (response.data && response.data.success) {
        return response.data; // Backend now controls attempts, lockout, captcha info
      } else {
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        await this.logAuditEvent({
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'Failed to request OTP.';
        console.error(`AuthService.requestOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: eventType + '_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        return { success: false, error: errorDetail, ...response.data }; // Spread data in case it has attempts/lockout info
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error during OTP request.';
      await this.logAuditEvent({
        eventType: eventType + '_failure',
        phoneNumber: phone,
        status: 'failure',
        details: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }

  async verifyOTP(phone: string, otp: string): Promise<VerificationResult> {
    // Client-side lockout logic REMOVED
    
    try {
      const response = await api.post<VerificationResult>('/auth/verify-otp', {
        phone,
        otp,
        device: this.getDeviceInfo(),
      });

      if (response.data && response.data.success && response.data.token) {
        localStorage.setItem('pvtelv_auth', 'true');
        localStorage.setItem('pvtelv_token', response.data.token);
        
        // Client-side failed attempts tracking REMOVED

        await this.logAuditEvent({
          eventType: 'otp_verification_success',
          phoneNumber: phone,
          userId: response.data.userId, // Assuming backend might return userId in token or response
          status: 'success',
        });

        // Welcome notification logic can remain for now, but ideally backend driven
        // Or triggered by a specific "isNewUser" flag from backend post-verification
        const isNewUser = !localStorage.getItem('pvtelv_welcomed'); // This is a crude way to check new user
        if (isNewUser) {
          localStorage.setItem('pvtelv_welcomed', 'true');
          // Assuming notificationService.sendWelcomeNotification doesn't need actual user ID immediately
          // or userId can be fetched from token later by the component calling this.
          await notificationService.sendWelcomeNotification(response.data.userId || 'unknown_user', phone);
        }
        
        return { success: true, token: response.data.token, userId: response.data.userId };
      } else {
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        await this.logAuditEvent({
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        const errorDetail = response.error || response.data?.error || 'OTP verification failed.';
        console.error(`AuthService.verifyOTP Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({ // logAuditEvent is already present and good
          eventType: 'otp_verification_failure',
          phoneNumber: phone,
          status: 'failure',
          details: errorDetail,
        });
        return { success: false, error: errorDetail };
      }
    } catch (error) { // Catch errors from api.post itself
      const errorMessage = error instanceof Error ? error.message : 'Unknown error during OTP verification.';
      await this.logAuditEvent({
        eventType: 'otp_verification_error',
        phoneNumber: phone,
        status: 'failure',
        details: errorMessage,
      });
      return { success: false, error: errorMessage };
    }
  }

  async logout(sessionId?: string): Promise<boolean> {
    const userIdFromToken = this.getUserIdFromToken(); // Helper to get user ID
    try {
      // Revoke current session on backend and clear local storage
      // Or if sessionId is provided, backend revokes that specific session
      const endpoint = sessionId ? `/auth/revoke-session/${sessionId}` : '/auth/logout';
      const payload = sessionId ? {} : {device: this.getDeviceInfo()}; // Logout might need current session info

      await api.post(endpoint, payload); // Assuming POST, adjust if different

      localStorage.removeItem('pvtelv_auth');
      localStorage.removeItem('pvtelv_token');
      localStorage.removeItem('pvtelv_welcomed'); // Clear welcome flag on logout too
      
      await this.logAuditEvent({
        eventType: 'logout',
        userId: userIdFromToken, // TODO: Get from token
        status: 'success',
      });
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error during logout.';
      await this.logAuditEvent({
        eventType: 'logout_error',
        userId: userIdFromToken, // TODO: Get from token
        status: 'failure',
        details: errorMessage,
      });
      // Even if backend call fails, attempt to clear local session for UX
      localStorage.removeItem('pvtelv_auth');
      localStorage.removeItem('pvtelv_token');
      localStorage.removeItem('pvtelv_welcomed');
      const apiResponse = await api.post(endpoint, payload); // Changed to capture response
      if (apiResponse.error) { 
        console.error(`AuthService.logout API Error: ${apiResponse.error}`, apiResponse); 
        await this.logAuditEvent({ eventType: 'logout_api_error', userId: userIdFromToken, status: 'failure', details: apiResponse.error });
        localStorage.removeItem('pvtelv_auth');
        localStorage.removeItem('pvtelv_token');
        localStorage.removeItem('pvtelv_welcomed');
        return false; 
      }
      localStorage.removeItem('pvtelv_auth');
      localStorage.removeItem('pvtelv_token');
      localStorage.removeItem('pvtelv_welcomed'); 
      
      await this.logAuditEvent({
        eventType: 'logout',
        userId: userIdFromToken, 
        status: 'success',
      });
      return true;
    } catch (error) { 
      const errorMessage = error instanceof Error ? error.message : 'Unknown error during logout.';
      // logAuditEvent is already called in the original code for this catch block.
      // The console.error for network/unexpected errors is handled by api.ts's own catch block.
      // So, the existing audit log here is sufficient for this specific error path.
      await this.logAuditEvent({
        eventType: 'logout_error', 
        userId: userIdFromToken, 
        status: 'failure',
        details: errorMessage,
      });
      localStorage.removeItem('pvtelv_auth');
      localStorage.removeItem('pvtelv_token');
      localStorage.removeItem('pvtelv_welcomed');
      return false; 
    }
  }

  async revokeAllOtherSessions(): Promise<boolean> {
    const userIdFromToken = this.getUserIdFromToken();
    try {
      const response = await api.post('/auth/revoke-all-sessions', {}); 
      
      if (response.data) { 
        await this.logAuditEvent({
          eventType: 'revoke_all_sessions',
          userId: userIdFromToken, 
          status: 'success',
        });
        return true;
      } else {
        const errorDetail = response.error || 'Failed to revoke other sessions.';
        console.error(`AuthService.revokeAllOtherSessions Error: ${errorDetail}`, response); // Added console.error
        await this.logAuditEvent({
          eventType: 'revoke_all_sessions_error',
          userId: userIdFromToken, 
          status: 'failure',
          details: errorDetail,
        });
        return false;
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error during session revocation.';
      await this.logAuditEvent({
        eventType: 'revoke_all_sessions_error',
        userId: userIdFromToken, // TODO: Get from token
        status: 'failure',
        details: errorMessage,
      });
      return false;
    }
  }

  isAuthenticated(): boolean {
    const token = this.getToken();
    // Basic check: token exists. Could add token expiry check here if not done by API calls.
    return !!token; 
  }

  getToken(): string | null {
    return localStorage.getItem('pvtelv_token');
  }

  // Placeholder for a helper that would parse JWT to get user ID
  // In a real app, use a library like jwt-decode
  private getUserIdFromToken(): string | undefined {
    const token = this.getToken();
    if (token) {
      try {
        // const decoded: { sub?: string, userId?: string, id?: string } = jwt_decode(token); // Example
        // return decoded.sub || decoded.userId || decoded.id;
        return "user_from_token_placeholder"; // Replace with actual token parsing
      } catch (e) {
        console.error("Failed to decode token:", e);
        return undefined;
      }
    }
    return undefined;
  }
}

export const authService = new AuthService();
