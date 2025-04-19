
import React from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { ProfileSetup } from "@/components/profile/ProfileSetup";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SessionManager, Session } from "@/components/auth/SessionManager";
import { useToast } from "@/hooks/use-toast";

const Profile = () => {
  const { toast } = useToast();
  
  // Mock data for demonstration
  const mockSessions: Session[] = [
    {
      id: "session-1",
      device: {
        type: "desktop",
        name: "Chrome on Windows",
        browser: "Chrome 94",
      },
      location: {
        city: "New York",
        country: "USA",
        ip: "192.168.1.1",
      },
      lastActive: new Date().toISOString(),
      current: true,
    },
    {
      id: "session-2",
      device: {
        type: "mobile",
        name: "Safari on iPhone",
        browser: "Safari 15",
      },
      location: {
        city: "Boston",
        country: "USA",
        ip: "192.168.1.2",
      },
      lastActive: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      current: false,
    },
  ];
  
  const handleProfileSubmit = (data: any) => {
    console.log("Profile data submitted:", data);
    toast({
      title: "Profile updated",
      description: "Your profile information has been saved.",
    });
  };
  
  const handleRevokeSession = (sessionId: string) => {
    console.log("Revoking session:", sessionId);
    toast({
      title: "Session revoked",
      description: "The session has been successfully terminated.",
    });
  };
  
  const handleRevokeAllOtherSessions = () => {
    console.log("Revoking all other sessions");
    toast({
      title: "All other sessions revoked",
      description: "All other devices have been logged out.",
    });
  };
  
  return (
    <DashboardLayout currentPath="/profile" userName="John Doe">
      <div className="space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Profile Settings</h1>
        
        <div className="grid gap-6 md:grid-cols-2">
          <div>
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
              </CardHeader>
              <CardContent>
                <ProfileSetup onSubmit={handleProfileSubmit} />
              </CardContent>
            </Card>
          </div>
          
          <div>
            <SessionManager
              sessions={mockSessions}
              onRevokeSession={handleRevokeSession}
              onRevokeAllOtherSessions={handleRevokeAllOtherSessions}
            />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Profile;
