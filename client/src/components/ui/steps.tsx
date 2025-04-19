
import React from "react";
import { cn } from "@/lib/utils";
import { Check } from "lucide-react";

interface Step {
  title: string;
  description?: string;
  isComplete: boolean;
  isCurrent: boolean;
}

interface StepsProps {
  steps: Step[];
  currentStep: number;
}

export function Steps({ steps, currentStep }: StepsProps) {
  return (
    <div className="flex flex-col space-y-6 md:space-y-0 md:flex-row md:space-x-4">
      {steps.map((step, index) => (
        <div
          key={index}
          className={cn(
            "flex flex-1 flex-col",
            index < steps.length - 1 &&
              "md:after:content-[''] md:after:w-full md:after:h-0.5 md:after:bg-muted md:after:mt-3",
            index > 0 && index < steps.length &&
              "md:before:content-[''] md:before:w-full md:before:h-0.5 md:before:bg-muted md:before:mt-3"
          )}
        >
          <div className="flex items-center">
            <div
              className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border",
                step.isComplete
                  ? "bg-wallet-success text-white border-wallet-success"
                  : step.isCurrent
                  ? "bg-wallet-primary text-white border-wallet-primary"
                  : "bg-background border-muted-foreground/20"
              )}
            >
              {step.isComplete ? (
                <Check className="h-4 w-4" />
              ) : (
                <span className="text-sm font-medium">{index + 1}</span>
              )}
            </div>
            <div className="ml-3">
              <p
                className={cn(
                  "text-sm font-medium",
                  step.isCurrent && "text-wallet-primary",
                  step.isComplete && "text-wallet-success"
                )}
              >
                {step.title}
              </p>
              {step.description && (
                <p className="text-xs text-muted-foreground mt-0.5">
                  {step.description}
                </p>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
