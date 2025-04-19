import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Smartphone, Laptop, LogOut, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { authService } from "@/services/auth";

export interface Session {
  id: string;
  device: {
    type: "mobile" | "desktop" | "tablet" | "unknown";
    name: string;
    browser: string;
  };
  location: {
    city?: string;
    country?: string;
    ip: string;
  };
  lastActive: string;
  current: boolean;
}

interface SessionManagerProps {
  sessions: Session[];
  onRevokeSession: (sessionId: string) => void;
  onRevokeAllOtherSessions: () => void;
}

export function SessionManager({
  sessions,
  onRevokeSession,
  onRevokeAllOtherSessions,
}: SessionManagerProps) {
  const getDeviceIcon = (type: string) => {
    switch (type) {
      case "mobile":
        return <Smartphone className="h-5 w-5" />;
      case "desktop":
      case "tablet":
      default:
        return <Laptop className="h-5 w-5" />;
    }
  };

  const currentSession = sessions.find((s) => s.current);
  const otherSessions = sessions.filter((s) => !s.current);

  const handleRevokeSession = async (sessionId: string) => {
    await authService.logout(sessionId);
    onRevokeSession(sessionId);
  };

  const handleRevokeAllOtherSessions = async () => {
    await authService.revokeAllOtherSessions();
    onRevokeAllOtherSessions();
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center">
          <Laptop className="h-5 w-5 mr-2 text-wallet-primary" />
          Active Sessions
        </CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {currentSession && (
          <div className="p-4 border rounded-md bg-muted/30">
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-wallet-primary/10 rounded-full text-wallet-primary">
                  {getDeviceIcon(currentSession.device.type)}
                </div>
                <div>
                  <h4 className="font-medium flex items-center">
                    {currentSession.device.name}
                    <span className="ml-2 px-1.5 py-0.5 text-xs bg-wallet-primary/20 text-wallet-primary rounded-md">
                      Current
                    </span>
                  </h4>
                  <p className="text-xs text-muted-foreground">
                    {currentSession.device.browser} • {currentSession.location.ip}
                  </p>
                </div>
              </div>
              <div className="flex items-center text-xs text-muted-foreground">
                <Clock className="h-3 w-3 mr-1" />
                Now
              </div>
            </div>
          </div>
        )}
        
        {otherSessions.length > 0 && (
          <>
            <h4 className="text-sm font-medium flex items-center justify-between">
              <span>Other sessions</span>
              <Button 
                variant="outline" 
                size="sm" 
                className="text-xs"
                onClick={handleRevokeAllOtherSessions}
              >
                <LogOut className="h-3 w-3 mr-1" />
                Logout All Other Devices
              </Button>
            </h4>
            
            <div className="space-y-3">
              {otherSessions.map((session) => (
                <div key={session.id} className="p-4 border rounded-md">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-muted rounded-full">
                        {getDeviceIcon(session.device.type)}
                      </div>
                      <div>
                        <h4 className="font-medium">{session.device.name}</h4>
                        <p className="text-xs text-muted-foreground">
                          {session.device.browser}
                          {session.location.city && ` • ${session.location.city}, ${session.location.country}`}
                        </p>
                        <p className="text-xs text-muted-foreground">{session.location.ip}</p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-end space-y-2">
                      <div className="flex items-center text-xs text-muted-foreground">
                        <Clock className="h-3 w-3 mr-1" />
                        Active {formatDistanceToNow(new Date(session.lastActive), { addSuffix: true })}
                      </div>
                      
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className="text-destructive text-xs"
                        onClick={() => handleRevokeSession(session.id)}
                      >
                        <LogOut className="h-3 w-3 mr-1" />
                        Logout
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
        
        {otherSessions.length === 0 && (
          <div className="p-8 text-center text-muted-foreground">
            <p>No other active sessions</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
