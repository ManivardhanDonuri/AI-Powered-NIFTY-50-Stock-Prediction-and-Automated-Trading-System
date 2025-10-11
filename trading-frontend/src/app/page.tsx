'use client';

import { useRouter } from 'next/navigation';
import LandingPage from '@/components/layout/LandingPage';

export default function Home() {
  const router = useRouter();

  const handleEnterDashboard = () => {
    router.push('/live-charts');
  };

  return <LandingPage onEnterDashboard={handleEnterDashboard} />;
}