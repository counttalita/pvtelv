
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Shield, ShieldCheck, Smartphone, Mail, Lock } from "lucide-react";

interface SecurityItem {
  id: string;
  title: string;
  completed: boolean;
  icon: React.ReactNode;
}

interface SecurityStatusProps {
  items: SecurityItem[];
  onSetupItem: (id: string) => void;
}

export function SecurityStatus({ items, onSetupItem }: SecurityStatusProps) {
  const completedItems = items.filter((item) => item.completed).length;
  const progressPercentage = (completedItems / items.length) * 100;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-wallet-dark to-wallet-accent pb-8">
        <div className="flex justify-between items-start">
          <CardTitle className="text-white flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Account Security
          </CardTitle>
          <div className="flex items-center bg-black/20 px-2 py-1 rounded-full">
            <ShieldCheck className="h-4 w-4 mr-1 text-white" />
            <span className="text-xs text-white font-medium">
              {completedItems}/{items.length} Complete
            </span>
          </div>
        </div>
        
        <div className="mt-6">
          <div className="flex justify-between text-xs text-white mb-1">
            <span>Security Status</span>
            <span>{Math.round(progressPercentage)}% Complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2 bg-white/20" />
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <ul className="divide-y">
          {items.map((item) => (
            <li key={item.id} className="flex items-center justify-between p-4">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${
                  item.completed ? "bg-wallet-success/10" : "bg-muted"
                }`}>
                  {item.icon}
                </div>
                <span className="font-medium">{item.title}</span>
              </div>
              
              {item.completed ? (
                <Button variant="ghost" size="sm" disabled className="text-wallet-success">
                  <ShieldCheck className="h-4 w-4 mr-1" />
                  Complete
                </Button>
              ) : (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => onSetupItem(item.id)}
                >
                  Set up
                </Button>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

export function DefaultSecurityItems() {
  return [
    {
      id: "2fa",
      title: "Two-Factor Authentication",
      completed: false,
      icon: <Smartphone className="h-4 w-4 text-wallet-primary" />,
    },
    {
      id: "email_verification",
      title: "Verify Email Address",
      completed: false,
      icon: <Mail className="h-4 w-4 text-wallet-primary" />,
    },
    {
      id: "secure_password",
      title: "Set Secure Password",
      completed: true,
      icon: <Lock className="h-4 w-4 text-wallet-success" />,
    },
  ];
}
