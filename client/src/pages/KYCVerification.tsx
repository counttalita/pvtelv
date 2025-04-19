
import React, { useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DocumentUpload } from "@/components/kyc/DocumentUpload";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Steps } from "@/components/ui/steps";
import { KYCStatus } from "@/components/kyc/KYCStatus";
import { useToast } from "@/hooks/use-toast";

const KYCVerification = () => {
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState({
    id_front: false,
    id_back: false,
    selfie: false,
  });

  const handleDocumentUpload = (type: "id_front" | "id_back" | "selfie", file: File) => {
    console.log(`Uploaded ${type} document:`, file.name);
    setUploadedDocs((prev) => ({ ...prev, [type]: true }));
  };

  const handleNext = () => {
    if (currentStep < 2) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = () => {
    setIsLoading(true);
    
    // In a real app, this would upload the documents to the backend
    setTimeout(() => {
      setIsLoading(false);
      setIsSubmitted(true);
      toast({
        title: "Verification submitted",
        description: "Your documents have been submitted for review.",
      });
    }, 2000);
  };

  const steps = [
    {
      title: "ID Card Front",
      description: "Upload the front of your government-issued ID",
    },
    {
      title: "ID Card Back",
      description: "Upload the back of your government-issued ID",
    },
    {
      title: "Selfie Verification",
      description: "Upload a selfie holding your ID card",
    },
  ];

  const isStepComplete = (step: number) => {
    switch (step) {
      case 0:
        return uploadedDocs.id_front;
      case 1:
        return uploadedDocs.id_back;
      case 2:
        return uploadedDocs.selfie;
      default:
        return false;
    }
  };

  const canProceed = isStepComplete(currentStep);

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <DocumentUpload
            documentType="id_front"
            onUpload={handleDocumentUpload}
            isUploaded={uploadedDocs.id_front}
          />
        );
      case 1:
        return (
          <DocumentUpload
            documentType="id_back"
            onUpload={handleDocumentUpload}
            isUploaded={uploadedDocs.id_back}
          />
        );
      case 2:
        return (
          <DocumentUpload
            documentType="selfie"
            onUpload={handleDocumentUpload}
            isUploaded={uploadedDocs.selfie}
          />
        );
      default:
        return null;
    }
  };

  if (isSubmitted) {
    return (
      <DashboardLayout currentPath="/kyc">
        <div className="max-w-2xl mx-auto space-y-6">
          <h1 className="text-2xl font-bold tracking-tight">Identity Verification</h1>
          
          <KYCStatus 
            status="pending_manual" 
            submittedAt={new Date().toISOString()}
          />
          
          <Card>
            <CardHeader>
              <CardTitle>What happens next?</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <p>Our team will review your submitted documents:</p>
              <ol className="list-decimal pl-5 space-y-2">
                <li>Document review usually takes 1-2 business days</li>
                <li>You will be notified by email when your verification is complete</li>
                <li>You may be asked to provide additional documents if needed</li>
              </ol>
              <p className="pt-2">
                You can check the status of your verification on the dashboard at any time.
              </p>
            </CardContent>
          </Card>
          
          <div className="flex justify-center">
            <Button 
              variant="outline" 
              onClick={() => window.location.href = "/dashboard"}
            >
              Return to Dashboard
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout currentPath="/kyc">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold tracking-tight">Identity Verification</h1>
        <p className="text-muted-foreground">
          Please complete the verification process to access all features of your wallet.
        </p>
        
        <Card className="overflow-hidden">
          <CardHeader className="bg-muted">
            <CardTitle>Document Verification</CardTitle>
            <CardDescription>
              Upload clear photos of your identification documents
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <div className="mb-6">
              <Steps
                steps={steps.map((step, index) => ({
                  title: step.title,
                  description: step.description,
                  isComplete: isStepComplete(index),
                  isCurrent: currentStep === index,
                }))}
                currentStep={currentStep}
              />
            </div>
            
            <Separator className="my-6" />
            
            <div className="space-y-4">
              <h3 className="text-lg font-medium">
                {steps[currentStep].title}
              </h3>
              <p className="text-sm text-muted-foreground">
                {steps[currentStep].description}
              </p>
              <div className="mt-4">{renderStepContent()}</div>
            </div>
            
            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={handleBack}
                disabled={currentStep === 0}
              >
                Back
              </Button>
              <Button
                onClick={handleNext}
                disabled={!canProceed}
                className="bg-wallet-primary hover:bg-wallet-accent"
              >
                {currentStep === steps.length - 1
                  ? isLoading
                    ? "Submitting..."
                    : "Submit for Verification"
                  : "Next"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default KYCVerification;
