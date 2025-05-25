import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallbackMessage?: string; // Optional custom message
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(_: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    // You could also send this to a logging service
    // logErrorToMyService(error, errorInfo.componentStack);
    this.setState({ error, errorInfo }); // Store error details if needed for display
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div role="alert" style={{ padding: '20px', textAlign: 'center', border: '1px solid red', margin: '20px' }}>
          <h2>{this.props.fallbackMessage || "Something went wrong."}</h2>
          <p>We're sorry for the inconvenience. Please try refreshing the page.</p>
          {/* Optionally, display more error details in development */}
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', marginTop: '10px' }}>
              {this.state.error.toString()}
              <br />
              {this.state.errorInfo?.componentStack}
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
