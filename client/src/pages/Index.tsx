import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CreditCard, Shield, ArrowRight, CheckCircle } from "lucide-react";

const Index = () => {
  const features = [
    {
      icon: <CreditCard className="h-6 w-6 text-wallet-primary" />,
      title: "Secure Digital Wallet",
      description:
        "Store and manage your digital assets with enterprise-grade security features.",
    },
    {
      icon: <Shield className="h-6 w-6 text-wallet-primary" />,
      title: "Advanced KYC",
      description:
        "Robust identity verification that meets regulatory compliance requirements.",
    },
    {
      icon: <CheckCircle className="h-6 w-6 text-wallet-primary" />,
      title: "Multi-Device Support",
      description:
        "Access your wallet securely from any device with comprehensive session management.",
    },
  ];

  return (
    <div className="min-h-screen bg-muted/30">
      <section className="relative bg-gradient-to-b from-wallet-dark via-wallet-primary/90 to-wallet-accent/80 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 md:py-32">
          <div className="md:flex md:items-center md:space-x-8">
            <div className="md:w-1/2 space-y-6">
              <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
                PVTELV Digital Wallet
              </h1>
              <p className="text-xl md:text-2xl text-white/80">
                A secure, mobile-first digital wallet with advanced security features and robust KYC integration.
              </p>
              <div className="space-x-4 pt-4">
                <Button 
                  size="lg" 
                  className="bg-white text-wallet-dark hover:bg-white/90"
                  asChild
                >
                  <Link to="/auth">Create Account</Link>
                </Button>
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="border-white text-white hover:bg-white/10"
                  asChild
                >
                  <Link to="/auth">Login</Link>
                </Button>
              </div>
            </div>
            <div className="hidden md:block md:w-1/2 mt-8 md:mt-0">
              <div className="relative h-64 w-full overflow-hidden rounded-2xl bg-gradient-to-br from-wallet-accent to-wallet-dark border border-white/20 shadow-xl">
                <div className="absolute top-4 left-4 right-4 h-8 rounded-lg bg-white/10 backdrop-blur-sm flex items-center px-3">
                  <div className="flex space-x-1">
                    <div className="h-2 w-2 rounded-full bg-white/40"></div>
                    <div className="h-2 w-2 rounded-full bg-white/40"></div>
                    <div className="h-2 w-2 rounded-full bg-white/40"></div>
                  </div>
                </div>
                <div className="absolute bottom-4 left-4 right-4 h-16 rounded-lg bg-white/10 backdrop-blur-sm p-3">
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="h-2.5 w-16 rounded-full bg-white/40 mb-2"></div>
                      <div className="h-2 w-24 rounded-full bg-white/30"></div>
                    </div>
                    <Button size="sm" className="h-8 bg-white text-wallet-primary hover:bg-white/90">
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold">Powerful Security Features</h2>
            <p className="mt-4 text-lg text-muted-foreground max-w-3xl mx-auto">
              PVTELV combines advanced security with a seamless user experience to keep your digital assets protected.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <Card key={i} className="overflow-hidden">
                <CardContent className="p-6">
                  <div className="h-12 w-12 rounded-full bg-wallet-primary/10 flex items-center justify-center mb-4">
                    {feature.icon}
                  </div>
                  <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
          
          <div className="mt-16 text-center">
            <Button 
              size="lg" 
              className="bg-wallet-primary hover:bg-wallet-accent"
              asChild
            >
              <Link to="/auth">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer section */}
      <footer className="bg-muted/50 border-t py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between md:flex-row">
            <div className="flex items-center">
              <CreditCard className="h-6 w-6 text-wallet-primary mr-2" />
              <span className="font-bold text-lg">PVTELV</span>
            </div>
            <div className="mt-4 md:mt-0 text-sm text-muted-foreground">
              © {new Date().getFullYear()} PVTELV. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
