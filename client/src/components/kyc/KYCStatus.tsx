
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, CheckCircle, AlertTriangle, HelpCircle } from "lucide-react";

type KYCStatusType = "pending_manual" | "approved" | "rejected" | "not_started";

interface KYCStatusProps {
  status: KYCStatusType;
  rejectionReason?: string;
  submittedAt?: string;
}

export function KYCStatus({ status, rejectionReason, submittedAt }: KYCStatusProps) {
  const renderIcon = () => {
    switch (status) {
      case "pending_manual":
        return <Clock className="h-8 w-8 text-wallet-warning" />;
      case "approved":
        return <CheckCircle className="h-8 w-8 text-wallet-success" />;
      case "rejected":
        return <AlertTriangle className="h-8 w-8 text-wallet-error" />;
      case "not_started":
        return <HelpCircle className="h-8 w-8 text-muted-foreground" />;
    }
  };

  const renderTitle = () => {
    switch (status) {
      case "pending_manual":
        return "Verification in Progress";
      case "approved":
        return "Verification Complete";
      case "rejected":
        return "Verification Failed";
      case "not_started":
        return "Verification Required";
    }
  };

  const renderDescription = () => {
    switch (status) {
      case "pending_manual":
        return "Your documents are being reviewed by our team. This usually takes 1-2 business days.";
      case "approved":
        return "Your identity has been verified. You now have full access to all wallet features.";
      case "rejected":
        return rejectionReason || "Your verification was unsuccessful. Please review the feedback and resubmit.";
      case "not_started":
        return "Complete identity verification to access all wallet features.";
    }
  };

  const renderBadge = () => {
    switch (status) {
      case "pending_manual":
        return <Badge className="bg-wallet-warning">Pending Review</Badge>;
      case "approved":
        return <Badge className="bg-wallet-success">Verified</Badge>;
      case "rejected":
        return <Badge variant="destructive">Failed</Badge>;
      case "not_started":
        return <Badge variant="outline">Not Started</Badge>;
    }
  };

  return (
    <Card className="border-l-4 bg-card/50 shadow-sm"
      style={{ 
        borderLeftColor: status === "approved" 
          ? "#10B981" 
          : status === "pending_manual" 
            ? "#F59E0B" 
            : status === "rejected" 
              ? "#EF4444" 
              : "#e5e7eb" 
      }}
    >
      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-medium">{renderTitle()}</CardTitle>
        {renderBadge()}
      </CardHeader>
      <CardContent>
        <div className="flex items-start space-x-4">
          <div className="mt-1">{renderIcon()}</div>
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{renderDescription()}</p>
            
            {submittedAt && status === "pending_manual" && (
              <p className="text-xs text-muted-foreground">
                Submitted on {new Date(submittedAt).toLocaleDateString()}
              </p>
            )}
            
            {status === "rejected" && (
              <div className="mt-2 p-3 bg-destructive/10 rounded-sm">
                <p className="text-sm font-medium text-destructive">
                  {rejectionReason || "Please check your documents and try again."}
                </p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
