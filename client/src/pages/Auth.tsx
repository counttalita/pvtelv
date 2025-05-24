import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CreditCard } from "lucide-react";
import { authService } from "@/services/auth";
import { PhoneInput } from "@/components/auth/PhoneInput";
import { OTPVerification } from "@/components/auth/OTPVerification";
// Removed Button, Input, Label as they are no longer used after password form removal

const Auth = () => {
  const navigate = useNavigate();
  const [authStep, setAuthStep] = useState<"phone" | "otp">("phone"); // Removed "password"
  const [phoneNumber, setPhoneNumber] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handlePhoneSubmit = async (phone: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const validation = await authService.validatePhone(phone);
      
      if (!validation.isValid || validation.isVoip) {
        setError("Invalid phone number or VoIP number detected");
        return;
      }
      
      const otpResult = await authService.requestOTP(phone);
      
      if (otpResult.success) {
        setPhoneNumber(phone);
        setAuthStep("otp");
      } else if (otpResult.requiresCaptcha) {
        setError("Please complete the CAPTCHA to continue");
      } else {
        setError("Failed to send verification code");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleOTPVerify = async (otp: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await authService.verifyOTP(phoneNumber, otp);
      
      if (result.success) { // authService already stored the token
        navigate("/dashboard");
      } else {
        setError(result.error || "Invalid verification code");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleOTPResend = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await authService.requestOTP(phoneNumber);
      if (!result.success) {
        setError("Failed to resend code. Please try again later.");
      }
    } catch (err) {
      setError("An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };
  
  // handlePasswordSubmit function REMOVED

  const renderAuthStep = () => {
    switch (authStep) {
      case "phone":
        return <PhoneInput onSubmit={handlePhoneSubmit} isLoading={isLoading} />;
      case "otp":
        return (
          <OTPVerification
            phoneNumber={phoneNumber}
            onVerify={handleOTPVerify}
            onResend={handleOTPResend}
            isLoading={isLoading}
          />
        );
      // case "password" block REMOVED
    }
  };
  
  return (
    <div className="flex justify-center items-center min-h-screen bg-gradient-to-b from-wallet-primary/5 to-white p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center space-y-1">
          <div className="flex justify-center mb-2">
            <div className="bg-wallet-primary text-white p-2 rounded-full">
              <CreditCard className="h-8 w-8" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">PVTELV Wallet</CardTitle>
          <p className="text-sm text-muted-foreground">
            Secure digital wallet with advanced protection
          </p>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="register" className="w-full">
            <TabsList className="grid grid-cols-2 mb-4">
              <TabsTrigger value="register">Register</TabsTrigger>
              <TabsTrigger value="login">Login</TabsTrigger>
            </TabsList>
            <TabsContent value="register" className="space-y-4">
              {renderAuthStep()}
            </TabsContent>
            <TabsContent value="login" className="space-y-4">
              <PhoneInput onSubmit={handlePhoneSubmit} isLoading={isLoading} />
              <p className="text-xs text-center text-muted-foreground mt-4">
                Enter your registered phone number to receive a login code
              </p>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="flex justify-center border-t p-4">
          <p className="text-xs text-center text-muted-foreground">
            By continuing, you agree to our{" "}
            <Link to="/terms" className="text-wallet-primary hover:underline">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link to="/privacy" className="text-wallet-primary hover:underline">
              Privacy Policy
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  );
};

export default Auth;
