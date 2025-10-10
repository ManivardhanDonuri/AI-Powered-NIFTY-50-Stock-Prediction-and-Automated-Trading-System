'use client';

import { useEnhancedTheme } from '@/components/providers/ThemeProvider';
import { ThemeConfig } from '@/types/theme';

export function useThemeConfig(): ThemeConfig {
  const { resolvedTheme, config } = useEnhancedTheme();
  return config[resolvedTheme];
}

export function useThemeColors() {
  const config = useThemeConfig();
  return config.colors;
}

export function useThemeSpacing() {
  const config = useThemeConfig();
  return config.spacing;
}

export function useThemeBorderRadius() {
  const config = useThemeConfig();
  return config.borderRadius;
}

export function useThemeShadows() {
  const config = useThemeConfig();
  return config.shadows;
}