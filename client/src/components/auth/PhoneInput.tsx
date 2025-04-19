
import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { AlertCircle, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface PhoneInputProps {
  onSubmit: (phoneNumber: string) => void;
  isLoading?: boolean;
}

export function PhoneInput({ onSubmit, isLoading = false }: PhoneInputProps) {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [isValid, setIsValid] = useState<boolean | null>(null);
  
  // Simple E.164 format validation (would be more robust in production)
  const validatePhoneNumber = (phone: string) => {
    const e164Regex = /^\+[1-9]\d{1,14}$/;
    return e164Regex.test(phone);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPhoneNumber(value);
    
    if (value.length > 8) {
      setIsValid(validatePhoneNumber(value));
    } else {
      setIsValid(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isValid) {
      onSubmit(phoneNumber);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="phone-number">Phone Number</Label>
        <div className="relative">
          <Input
            id="phone-number"
            type="tel"
            placeholder="+12345678901"
            value={phoneNumber}
            onChange={handleChange}
            className={cn(
              "pr-10",
              isValid === true && "border-wallet-success",
              isValid === false && "border-wallet-error"
            )}
          />
          {isValid === true && (
            <Check className="absolute right-3 top-2.5 h-5 w-5 text-wallet-success" />
          )}
          {isValid === false && (
            <AlertCircle className="absolute right-3 top-2.5 h-5 w-5 text-wallet-error" />
          )}
        </div>
        {isValid === false && (
          <p className="text-sm text-wallet-error">
            Please enter a valid phone number in E.164 format (e.g., +12345678901)
          </p>
        )}
      </div>
      <Button 
        type="submit" 
        disabled={!isValid || isLoading} 
        className="w-full bg-wallet-primary hover:bg-wallet-accent"
      >
        {isLoading ? "Verifying..." : "Continue"}
      </Button>
    </form>
  );
}
