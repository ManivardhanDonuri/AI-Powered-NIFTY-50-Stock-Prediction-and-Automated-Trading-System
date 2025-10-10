'use client';

import { useState } from 'react';
import Button from './Button';
import Card from './Card';
import Input from './Input';
import Alert from './Alert';
import { Search, User, Mail } from 'lucide-react';

const ComponentShowcase = () => {
  const [inputValue, setInputValue] = useState('');
  const [inputError, setInputError] = useState('');
  const [showAlerts, setShowAlerts] = useState({
    success: true,
    warning: true,
    error: true,
    info: true,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
    if (e.target.value.length < 3 && e.target.value.length > 0) {
      setInputError('Must be at least 3 characters');
    } else {
      setInputError('');
    }
  };

  return (
    <div className="p-8 space-y-8 bg-[var(--color-background)] min-h-screen">
      <h1 className="text-3xl font-bold text-[var(--color-text-primary)] mb-8">
        Enhanced UI Components Showcase
      </h1>

      {/* Button Variants */}
      <Card variant="elevated" padding="lg">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
          Button Variants
        </h2>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" size="sm">Primary Small</Button>
            <Button variant="primary" size="md">Primary Medium</Button>
            <Button variant="primary" size="lg">Primary Large</Button>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="danger">Danger</Button>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button variant="primary" loading>Loading</Button>
            <Button variant="secondary" disabled>Disabled</Button>
            <Button variant="outline" icon={<User />}>With Icon</Button>
          </div>
        </div>
      </Card>

      {/* Card Variants */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card variant="default" padding="md">
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-2">
            Default Card
          </h3>
          <p className="text-[var(--color-text-secondary)]">
            This is a default card with medium padding and standard styling.
          </p>
        </Card>

        <Card variant="elevated" padding="lg">
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-2">
            Elevated Card
          </h3>
          <p className="text-[var(--color-text-secondary)]">
            This card has elevated styling with enhanced shadows.
          </p>
        </Card>

        <Card variant="outlined" padding="sm">
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-2">
            Outlined Card
          </h3>
          <p className="text-[var(--color-text-secondary)]">
            This card uses outlined styling with small padding.
          </p>
        </Card>
      </div>

      {/* Input Variants */}
      <Card variant="default" padding="lg">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
          Input Variants
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Input
              variant="default"
              label="Default Input"
              placeholder="Enter text..."
              helperText="This is a default input field"
            />
            
            <Input
              variant="filled"
              label="Filled Input"
              placeholder="Enter text..."
              helperText="This is a filled input field"
            />
            
            <Input
              variant="outlined"
              label="Outlined Input"
              placeholder="Enter text..."
              helperText="This is an outlined input field"
            />
          </div>
          
          <div className="space-y-4">
            <Input
              variant="default"
              label="With Left Icon"
              placeholder="Search..."
              icon={<Search />}
              iconPosition="left"
            />
            
            <Input
              variant="filled"
              label="With Right Icon"
              placeholder="Enter email..."
              icon={<Mail />}
              iconPosition="right"
            />
            
            <Input
              variant="outlined"
              label="With Validation"
              placeholder="Type at least 3 characters..."
              value={inputValue}
              onChange={handleInputChange}
              error={inputError}
            />
          </div>
        </div>
      </Card>

      {/* Alert Variants */}
      <Card variant="elevated" padding="lg">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
          Alert Variants
        </h2>
        <div className="space-y-4">
          {/* Success Alerts */}
          {showAlerts.success && (
            <Alert
              variant="success"
              title="Trade Executed Successfully"
              message="Your BUY order for RELIANCE has been executed at ₹2,847.50"
              dismissible
              onDismiss={() => setShowAlerts(prev => ({ ...prev, success: false }))}
            />
          )}
          
          {/* Warning Alerts */}
          {showAlerts.warning && (
            <Alert
              variant="warning"
              title="Market Volatility Alert"
              message="High volatility detected in NIFTY 50. Consider reviewing your positions."
              dismissible
              onDismiss={() => setShowAlerts(prev => ({ ...prev, warning: false }))}
            />
          )}
          
          {/* Error Alerts */}
          {showAlerts.error && (
            <Alert
              variant="error"
              title="Connection Error"
              message="Unable to connect to trading server. Please check your internet connection."
              dismissible
              onDismiss={() => setShowAlerts(prev => ({ ...prev, error: false }))}
            />
          )}
          
          {/* Info Alerts */}
          {showAlerts.info && (
            <Alert
              variant="info"
              title="Model Training Complete"
              message="LSTM model for TCS has been retrained with 84.7% accuracy."
              dismissible
              onDismiss={() => setShowAlerts(prev => ({ ...prev, info: false }))}
            />
          )}
          
          {/* Size Variants */}
          <div className="space-y-3 pt-4 border-t border-[var(--color-border)]">
            <h3 className="text-lg font-medium text-[var(--color-text-primary)]">Size Variants</h3>
            <Alert
              variant="success"
              size="sm"
              message="Small alert for compact notifications"
            />
            <Alert
              variant="info"
              size="md"
              title="Medium Alert"
              message="Standard size alert with title and message"
            />
            <Alert
              variant="warning"
              size="lg"
              title="Large Alert"
              message="Large alert for important notifications that need more attention"
            />
          </div>
          
          {/* Custom Content */}
          <div className="pt-4 border-t border-[var(--color-border)]">
            <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-3">Custom Content</h3>
            <Alert variant="info" title="Trading Signal Generated" message="">
              <div className="space-y-2">
                <p>A new BUY signal has been generated for <strong>HDFCBANK</strong></p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="bg-[var(--color-success)]/10 text-[var(--color-success)] px-2 py-1 rounded">
                    Confidence: 87.3%
                  </span>
                  <span className="bg-[var(--color-info)]/10 text-[var(--color-info)] px-2 py-1 rounded">
                    Price: ₹1,642.75
                  </span>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button variant="primary" size="sm">Execute Trade</Button>
                  <Button variant="outline" size="sm">View Details</Button>
                </div>
              </div>
            </Alert>
          </div>
          
          {/* Reset Button */}
          <div className="pt-4 border-t border-[var(--color-border)]">
            <Button 
              variant="outline" 
              onClick={() => setShowAlerts({ success: true, warning: true, error: true, info: true })}
            >
              Reset All Alerts
            </Button>
          </div>
        </div>
      </Card>

      {/* Theme Integration Demo */}
      <Card variant="elevated" padding="lg">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)] mb-4">
          Theme Integration
        </h2>
        <p className="text-[var(--color-text-secondary)] mb-4">
          All components automatically adapt to the current theme using CSS custom properties.
          Try switching between light and dark modes to see the components update seamlessly.
        </p>
        <div className="flex gap-3">
          <Button variant="primary">Primary Action</Button>
          <Button variant="outline">Secondary Action</Button>
        </div>
      </Card>
    </div>
  );
};

export default ComponentShowcase;