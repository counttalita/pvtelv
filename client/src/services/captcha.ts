
import { api } from './api';

export interface CaptchaVerification {
  success: boolean;
  score?: number; // For reCAPTCHA v3
  error?: string;
  challengeTs?: string;
}

class CaptchaService {
  async verifyCaptcha(token: string, action?: string): Promise<CaptchaVerification> {
    const response = await api.post<CaptchaVerification>('/captcha/verify', {
      token,
      action
    });
    
    // Mock response
    return {
      success: true,
      score: 0.9,
      challengeTs: new Date().toISOString()
    };
  }

  async shouldShowCaptcha(userId?: string, ip?: string, attempts?: number): Promise<boolean> {
    // In a real scenario, this would check:
    // 1. Number of failed attempts
    // 2. IP reputation
    // 3. User history
    // 4. Time pattern (e.g., too many attempts in short time)
    
    if (attempts && attempts > 2) {
      return true;
    }
    
    return false;
  }
}

export const captchaService = new CaptchaService();
