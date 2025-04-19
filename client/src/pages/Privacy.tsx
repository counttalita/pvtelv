
import React from "react";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";

const Privacy = () => {
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

        <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>

        <div className="space-y-8 text-muted-foreground">
          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">1. Information We Collect</h2>
            <div className="space-y-4">
              <p>We collect information to provide better services to our users:</p>
              <h3 className="font-medium text-foreground">Personal Information:</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Name and contact information</li>
                <li>Government-issued identification</li>
                <li>Phone numbers</li>
                <li>Email addresses</li>
                <li>Banking information</li>
              </ul>
              
              <h3 className="font-medium text-foreground">Usage Information:</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Device information</li>
                <li>Log data</li>
                <li>Location information</li>
                <li>Transaction history</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">2. How We Use Your Information</h2>
            <p className="mb-4">We use the collected information for:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Providing and maintaining the Service</li>
              <li>Processing transactions</li>
              <li>Complying with legal requirements</li>
              <li>Verifying your identity</li>
              <li>Detecting and preventing fraud</li>
              <li>Improving our services</li>
              <li>Customer support</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">3. Information Sharing</h2>
            <p className="mb-4">We may share your information with:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Service providers and partners</li>
              <li>Financial institutions</li>
              <li>Legal authorities when required</li>
              <li>Third parties with your consent</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">4. Data Security</h2>
            <p className="mb-4">We implement appropriate security measures to protect your information:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Encryption of data in transit and at rest</li>
              <li>Regular security assessments</li>
              <li>Access controls and monitoring</li>
              <li>Secure data storage practices</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">5. Your Rights and Choices</h2>
            <p className="mb-4">You have the right to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Access your personal information</li>
              <li>Correct inaccurate data</li>
              <li>Request deletion of your data</li>
              <li>Object to data processing</li>
              <li>Data portability</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">6. Cookies and Tracking</h2>
            <p className="mb-4">We use cookies and similar technologies to:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Remember your preferences</li>
              <li>Analyze usage patterns</li>
              <li>Enhance security</li>
              <li>Improve user experience</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">7. Children's Privacy</h2>
            <p className="mb-4">Our Service is not intended for children under 18. We do not knowingly collect information from children under 18.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">8. International Data Transfers</h2>
            <p className="mb-4">Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place for such transfers.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">9. Changes to Privacy Policy</h2>
            <p className="mb-4">We may update this Privacy Policy periodically. We will notify you of any significant changes.</p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-foreground mb-4">10. Contact Us</h2>
            <p className="mb-4">For privacy-related inquiries, please contact our Data Protection Officer at privacy@pvtelv.com</p>
          </section>
        </div>

        <div className="mt-8 text-sm text-muted-foreground">
          Last updated: {new Date().toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

export default Privacy;
