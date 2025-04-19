
import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface OTPVerificationProps {
  phoneNumber: string;
  onVerify: (otp: string) => void;
  onResend: () => void;
  isLoading?: boolean;
}

export function OTPVerification({
  phoneNumber,
  onVerify,
  onResend,
  isLoading = false,
}: OTPVerificationProps) {
  const [otp, setOtp] = useState("");
  const [countdown, setCountdown] = useState(30);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (countdown > 0 && !canResend) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    } else {
      setCanResend(true);
    }
    return () => clearTimeout(timer);
  }, [countdown, canResend]);

  const handleResend = () => {
    onResend();
    setCanResend(false);
    setCountdown(30);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.length >= 4) {
      onVerify(otp);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Verification Code</h3>
        <p className="text-sm text-muted-foreground">
          We've sent a verification code to {phoneNumber}
        </p>
      </div>
      <div className="space-y-2">
        <Label htmlFor="otp">Enter Verification Code</Label>
        <Input
          id="otp"
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={6}
          placeholder="123456"
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
          className="text-center text-lg tracking-widest"
        />
      </div>
      <div className="space-y-2">
        <Button
          type="submit"
          disabled={otp.length < 4 || isLoading}
          className="w-full bg-wallet-primary hover:bg-wallet-accent"
        >
          {isLoading ? "Verifying..." : "Verify"}
        </Button>
        <div className="text-center mt-2">
          <Button
            type="button"
            variant="ghost"
            onClick={handleResend}
            disabled={!canResend}
            className="text-sm"
          >
            {canResend
              ? "Resend Code"
              : `Resend code in ${countdown} seconds`}
          </Button>
        </div>
      </div>
    </form>
  );
}
