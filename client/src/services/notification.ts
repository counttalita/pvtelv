
import { api } from './api';

export interface Notification {
  id: string;
  userId: string;
  type: 'welcome' | 'security' | 'transaction' | 'system';
  title: string;
  message: string;
  read: boolean;
  createdAt: string;
  channel?: 'in-app' | 'email' | 'sms' | 'push';
}

export interface NotificationResponse {
  notifications: Notification[];
  unreadCount: number;
}

class NotificationService {
  async getNotifications(userId: string): Promise<NotificationResponse> {
    const response = await api.fetch<NotificationResponse>(`/notifications/${userId}`);
    
    // Mock response
    return {
      notifications: [
        {
          id: '1',
          userId,
          type: 'welcome',
          title: 'Welcome to PVTELV Wallet',
          message: 'Thank you for joining PVTELV Wallet. Complete your profile to get started.',
          read: false,
          createdAt: new Date().toISOString(),
          channel: 'in-app'
        },
        {
          id: '2',
          userId,
          type: 'security',
          title: 'Security Setup',
          message: 'Enhance your account security by setting up additional verification methods.',
          read: false,
          createdAt: new Date().toISOString(),
          channel: 'in-app'
        }
      ],
      unreadCount: 2
    };
  }

  async sendWelcomeNotification(userId: string, phoneNumber: string): Promise<boolean> {
    const response = await api.post('/notifications/send', {
      userId,
      type: 'welcome',
      title: 'Welcome to PVTELV Wallet',
      message: 'Thank you for joining PVTELV Wallet. Complete your profile to get started.',
      channels: ['in-app', 'sms', 'email']
    });
    
    console.log(`Welcome notification sent to ${phoneNumber}`);
    return true;
  }

  async markAsRead(notificationId: string): Promise<boolean> {
    const response = await api.post('/notifications/mark-read', { 
      notificationId 
    });
    return true;
  }
}

export const notificationService = new NotificationService();
