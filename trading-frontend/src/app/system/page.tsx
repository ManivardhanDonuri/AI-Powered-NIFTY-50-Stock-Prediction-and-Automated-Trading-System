'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Alert from '@/components/ui/Alert';
import { 
  Play, 
  Square, 
  RotateCcw, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Cpu,
  Database,
  Wifi,
  HardDrive
} from 'lucide-react';

interface SystemStatus {
  running: boolean;
  uptime: number;
  lastUpdate: Date;
  errors: string[];
  warnings: string[];
  performance: {
    cpu: number;
    memory: number;
    disk: number;
  };
  services: {
    dataFetcher: boolean;
    signalGenerator: boolean;
    mlModels: boolean;
    database: boolean;
  };
}

export default function SystemPage() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    running: true,
    uptime: 3600, // 1 hour in seconds
    lastUpdate: new Date(),
    errors: [],
    warnings: ['High memory usage detected', 'Model accuracy below threshold for SBIN.NS'],
    performance: {
      cpu: 45,
      memory: 78,
      disk: 23,
    },
    services: {
      dataFetcher: true,
      signalGenerator: true,
      mlModels: true,
      database: true,
    },
  });

  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [logs, setLogs] = useState<string[]>([
    '[2024-01-15 10:30:15] System started successfully',
    '[2024-01-15 10:30:16] Data fetcher initialized',
    '[2024-01-15 10:30:17] ML models loaded',
    '[2024-01-15 10:30:18] Signal generator ready',
    '[2024-01-15 10:31:22] Generated BUY signal for RELIANCE.NS',
    '[2024-01-15 10:32:45] Generated SELL signal for TCS.NS',
    '[2024-01-15 10:33:12] Model training completed for HDFCBANK.NS',
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        uptime: prev.uptime + 1,
        lastUpdate: new Date(),
        performance: {
          cpu: Math.max(20, Math.min(80, prev.performance.cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(30, Math.min(90, prev.performance.memory + (Math.random() - 0.5) * 5)),
          disk: Math.max(10, Math.min(50, prev.performance.disk + (Math.random() - 0.5) * 2)),
        },
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setIsStarting(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSystemStatus(prev => ({ ...prev, running: true, uptime: 0 }));
      setLogs(prev => [...prev, `[${new Date().toLocaleString()}] System started`]);
    } catch (error) {
      console.error('Failed to start system:', error);
    } finally {
      setIsStarting(false);
    }
  };

  const handleStop = async () => {
    setIsStopping(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSystemStatus(prev => ({ ...prev, running: false }));
      setLogs(prev => [...prev, `[${new Date().toLocaleString()}] System stopped`]);
    } catch (error) {
      console.error('Failed to stop system:', error);
    } finally {
      setIsStopping(false);
    }
  };

  const handleRestart = async () => {
    await handleStop();
    await new Promise(resolve => setTimeout(resolve, 1000));
    await handleStart();
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}h ${minutes}m ${secs}s`;
  };

  const getStatusColor = (running: boolean) => {
    return running ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
  };

  const getPerformanceColor = (value: number) => {
    if (value < 50) return 'bg-green-500';
    if (value < 80) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 
              className="text-3xl font-bold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              System Control
            </h1>
            <p 
              className="mt-2"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Monitor and control your trading system
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {!systemStatus.running ? (
              <Button 
                onClick={handleStart}
                loading={isStarting}
                className="flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Start System</span>
              </Button>
            ) : (
              <>
                <Button 
                  variant="outline"
                  onClick={handleRestart}
                  disabled={isStarting || isStopping}
                  className="flex items-center space-x-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Restart</span>
                </Button>
                <Button 
                  variant="danger"
                  onClick={handleStop}
                  loading={isStopping}
                  className="flex items-center space-x-2"
                >
                  <Square className="w-4 h-4" />
                  <span>Stop System</span>
                </Button>
              </>
            )}
          </div>
        </div>

        {/* System Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  System Status
                </p>
                <p className={`text-2xl font-bold ${getStatusColor(systemStatus.running)}`}>
                  {systemStatus.running ? 'Running' : 'Stopped'}
                </p>
              </div>
              <div className={`p-3 rounded-full ${systemStatus.running ? 'bg-green-100 dark:bg-green-900/20' : 'bg-red-100 dark:bg-red-900/20'}`}>
                {systemStatus.running ? (
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
                )}
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Uptime
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {formatUptime(systemStatus.uptime)}
                </p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-full">
                <Clock className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Active Services
                </p>
                <p 
                  className="text-2xl font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {Object.values(systemStatus.services).filter(Boolean).length}/4
                </p>
              </div>
              <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-full">
                <Activity className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p 
                  className="text-sm font-medium"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  Last Update
                </p>
                <p 
                  className="text-lg font-bold"
                  style={{ color: 'var(--color-text-primary)' }}
                >
                  {systemStatus.lastUpdate.toLocaleTimeString()}
                </p>
              </div>
              <div className="p-3 bg-orange-100 dark:bg-orange-900/20 rounded-full">
                <Wifi className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
          </Card>
        </div>

        {/* Alerts */}
        {systemStatus.errors.length > 0 && (
          <Alert
            variant="error"
            title="System Errors"
            message={systemStatus.errors.join(', ')}
          />
        )}
        {systemStatus.warnings.length > 0 && (
          <Alert
            variant="warning"
            title="System Warnings"
            message={systemStatus.warnings.join(', ')}
          />
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Metrics */}
          <Card>
            <h3 
              className="text-xl font-semibold mb-6"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Performance Metrics
            </h3>
            
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Cpu className="w-5 h-5 text-gray-400" />
                  <span 
                    className="text-sm font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    CPU Usage
                  </span>
                </div>
                <span 
                  className="text-sm"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  {systemStatus.performance.cpu}%
                </span>
              </div>
              <div 
                className="w-full rounded-full h-2"
                style={{ backgroundColor: 'var(--color-border)' }}
              >
                <div 
                  className={`h-2 rounded-full ${getPerformanceColor(systemStatus.performance.cpu)}`}
                  style={{ width: `${systemStatus.performance.cpu}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Database className="w-5 h-5 text-gray-400" />
                  <span 
                    className="text-sm font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Memory Usage
                  </span>
                </div>
                <span 
                  className="text-sm"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  {systemStatus.performance.memory}%
                </span>
              </div>
              <div 
                className="w-full rounded-full h-2"
                style={{ backgroundColor: 'var(--color-border)' }}
              >
                <div 
                  className={`h-2 rounded-full ${getPerformanceColor(systemStatus.performance.memory)}`}
                  style={{ width: `${systemStatus.performance.memory}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <HardDrive className="w-5 h-5 text-gray-400" />
                  <span 
                    className="text-sm font-medium"
                    style={{ color: 'var(--color-text-primary)' }}
                  >
                    Disk Usage
                  </span>
                </div>
                <span 
                  className="text-sm"
                  style={{ color: 'var(--color-text-secondary)' }}
                >
                  {systemStatus.performance.disk}%
                </span>
              </div>
              <div 
                className="w-full rounded-full h-2"
                style={{ backgroundColor: 'var(--color-border)' }}
              >
                <div 
                  className={`h-2 rounded-full ${getPerformanceColor(systemStatus.performance.disk)}`}
                  style={{ width: `${systemStatus.performance.disk}%` }}
                ></div>
              </div>
            </div>
          </Card>

          {/* Service Status */}
          <Card>
            <h3 
              className="text-xl font-semibold mb-6"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Service Status
            </h3>
            
            <div className="space-y-4">
              {Object.entries(systemStatus.services).map(([service, status]) => (
                <div 
                  key={service} 
                  className="flex items-center justify-between p-3 rounded-lg"
                  style={{ backgroundColor: 'var(--color-surface)' }}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${status ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span 
                      className="font-medium capitalize"
                      style={{ color: 'var(--color-text-primary)' }}
                    >
                      {service.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                  </div>
                  <span className={`text-sm font-medium ${status ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {status ? 'Running' : 'Stopped'}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* System Logs */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <h3 
              className="text-xl font-semibold"
              style={{ color: 'var(--color-text-primary)' }}
            >
              System Logs
            </h3>
            <Button variant="outline" size="sm">
              Clear Logs
            </Button>
          </div>
          
          <div 
            className="rounded-lg p-4 h-64 overflow-y-auto"
            style={{ 
              backgroundColor: 'var(--color-text-primary)', 
              color: 'var(--color-success)' 
            }}
          >
            <div className="font-mono text-sm space-y-1">
              {logs.slice(-20).map((log, index) => (
                <div key={index} className="text-green-400">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}