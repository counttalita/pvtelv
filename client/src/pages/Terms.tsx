
import React from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

const Terms = () => {
  return (
    <div className="min-h-screen bg-muted/30 px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <Button variant="ghost" asChild>
            <Link to="/auth" className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Login
            </Link>
          </Button>
        </div>
        
        <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
        
        <div className="space-y-8 text-muted-foreground">
          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">1. Acceptance of Terms</h2>
            <p className="mb-4">By accessing and using PVTELV Wallet ("Service"), you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of the terms, you do not have permission to access the Service.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">2. Description of Service</h2>
            <p className="mb-4">PVTELV Wallet is a digital wallet service that allows users to manage digital assets securely. The Service includes account management, digital asset storage, and related features.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">3. User Registration and Security</h2>
            <p className="mb-4">You must complete the registration process by providing accurate, current, and complete information. You are responsible for maintaining the confidentiality of your account and password.</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>You must be at least 18 years old to use the Service</li>
              <li>You are responsible for all activities under your account</li>
              <li>You must notify us immediately of any security breach</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">4. KYC Requirements</h2>
            <p className="mb-4">Users must complete Know Your Customer (KYC) verification to access full service features. This includes providing valid identification documents and other required information.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">5. Service Rules and Limitations</h2>
            <p className="mb-4">Users agree not to engage in any of the following prohibited activities:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Violating laws or regulations</li>
              <li>Providing false or misleading information</li>
              <li>Attempting to gain unauthorized access</li>
              <li>Interfering with the Service's security features</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">6. Privacy and Data Protection</h2>
            <p className="mb-4">Our collection and use of personal information is governed by our Privacy Policy. By using the Service, you consent to such collection and use.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">7. Service Modifications</h2>
            <p className="mb-4">We reserve the right to modify or discontinue the Service at any time, with or without notice. We shall not be liable to you or any third party for any modification, suspension, or discontinuance.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">8. Termination</h2>
            <p className="mb-4">We may terminate or suspend your account immediately, without prior notice, for conduct that we believe violates these Terms or is harmful to other users, us, or third parties.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">9. Limitation of Liability</h2>
            <p className="mb-4">To the maximum extent permitted by law, PVTELV Wallet shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use or inability to use the Service.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">10. Contact Information</h2>
            <p className="mb-4">For questions about these Terms, please contact us at support@pvtelv.com</p>
          </section>
        </div>

        <div className="mt-8 text-sm text-muted-foreground">
          Last updated: {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default Terms;
