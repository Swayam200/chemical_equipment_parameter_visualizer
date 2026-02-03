import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("Uncaught error:", error, errorInfo);
        this.setState({ error, errorInfo });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-10 text-red-600 bg-red-50 h-screen overflow-auto">
                    <h1 className="text-2xl font-bold mb-4">Something went wrong.</h1>
                    <p className="font-mono text-sm mb-4">{this.state.error && this.state.error.toString()}</p>
                    <pre className="font-mono text-xs p-4 bg-gray-100 rounded">{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
