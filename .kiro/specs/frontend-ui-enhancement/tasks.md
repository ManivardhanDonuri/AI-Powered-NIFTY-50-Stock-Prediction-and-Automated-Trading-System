# Implementation Plan

- [x] 1. Set up enhanced theme system foundation





  - Create comprehensive CSS custom properties for light and dark themes in globals.css
  - Implement theme configuration objects with complete color palettes and design tokens
  - Update the existing ThemeProvider to support enhanced theme configurations
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2_

- [x] 2. Create reusable base UI components with theme integration





  - [x] 2.1 Enhance the existing Button component with variants and theme integration


    - Add support for primary, secondary, outline, ghost, and danger variants
    - Implement size variants (sm, md, lg) with proper spacing and typography
    - Add loading and disabled states with appropriate visual feedback
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2_

  - [x] 2.2 Enhance the existing Card component with theme-aware styling


    - Implement default, elevated, and outlined variants
    - Add configurable padding options (none, sm, md, lg)
    - Ensure proper background and border colors for both themes
    - _Requirements: 1.1, 1.2, 2.1, 2.2_

  - [x] 2.3 Enhance the existing Input component with comprehensive styling


    - Add default, filled, and outlined variants
    - Implement proper error states with validation styling
    - Add label and icon support with theme-aware colors
    - _Requirements: 1.1, 1.2, 2.1, 2.2_

  - [ ]* 2.4 Write unit tests for enhanced base components




    - Test component variants and prop combinations
    - Test theme integration and color application
    - Test accessibility features and keyboard navigation
    - _Requirements: 1.1, 1.2, 2.1_

- [x] 3. Update layout components with enhanced theme system





  - [x] 3.1 Enhance the Header component with complete theme integration


    - Update all styling to use CSS custom properties instead of hardcoded Tailwind classes
    - Ensure proper theme switching affects all header elements including backgrounds and text
    - Integrate enhanced theme toggle component with proper state management
    - _Requirements: 3.1, 3.2, 3.3, 5.1, 5.2_

  - [x] 3.2 Update the Sidebar component with theme-aware styling


    - Replace hardcoded colors with CSS custom properties
    - Implement proper hover and active states for both themes
    - Ensure navigation icons and text adapt to theme changes
    - _Requirements: 3.1, 3.2, 5.1, 5.2_

  - [x] 3.3 Enhance the DashboardLayout component for consistent theming


    - Update background colors and layout styling to use theme variables
    - Ensure proper theme propagation to all child components
    - Implement responsive theme behavior for mobile and desktop
    - _Requirements: 3.1, 3.2, 5.1, 5.3_
-

- [x] 4. Implement comprehensive theme toggle functionality




  - [x] 4.1 Create enhanced ThemeToggle component with complete website theming


    - Replace the existing theme toggle to affect entire website, not just charts
    - Implement smooth transitions between light and dark modes
    - Add proper accessibility attributes and keyboard support2
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [x] 4.2 Implement theme persistence and state management


    - Ensure theme preference is saved to localStorage and persists across sessions
    - Handle SSR hydration properly to prevent theme flashing
    - Implement proper theme detection and fallback mechanisms
    - _Requirements: 3.4, 3.5, 4.1, 4.2_

- [x] 5. Update chart components with enhanced theme integration





  - [x] 5.1 Modify TradingChart component to use centralized theme system


    - Update chart styling to consume theme colors from CSS custom properties
    - Ensure chart backgrounds, grid lines, and text adapt to theme changes
    - Implement proper theme switching for all chart elements
    - _Requirements: 3.6, 4.2, 4.3_

  - [x] 5.2 Update LivePriceChart and other chart components


    - Apply consistent theme integration across all chart components
    - Ensure proper color coordination between charts and UI elements
    - Implement theme-aware chart legends and tooltips
    - _Requirements: 3.6, 4.2, 4.3_

- [x] 6. Enhance feature components with reusable base components





  - [x] 6.1 Update ModelPerformance component to use enhanced UI components


    - Replace custom styling with reusable Card and Button components
    - Implement proper theme integration for performance metrics display
    - Ensure consistent spacing and typography using design tokens
    - _Requirements: 1.1, 1.3, 2.1, 2.2, 5.1_

  - [x] 6.2 Update StockSelector and other feature components


    - Refactor to use enhanced Input and Button components
    - Implement consistent styling patterns across all feature components
    - Ensure proper theme integration and responsive behavior
    - _Requirements: 1.1, 1.3, 2.1, 2.2, 5.1_

- [x] 7. Implement notification and alert components with theme integration





  - [x] 7.1 Update NotificationCenter component with enhanced styling


    - Apply theme-aware colors for different notification types (success, warning, error)
    - Implement proper contrast ratios for accessibility compliance
    - Use enhanced Card component as base for notification items
    - _Requirements: 2.3, 4.2, 4.3_

  - [x] 7.2 Enhance Alert component with comprehensive variant system


    - Implement success, warning, error, and info variants with proper theming
    - Add dismissible functionality with theme-aware close buttons
    - Ensure proper accessibility attributes and keyboard navigation
    - _Requirements: 1.1, 2.3, 4.2_

- [x] 8. Optimize and finalize theme system implementation





  - [x] 8.1 Implement CSS custom property optimization


    - Ensure efficient CSS custom property usage to minimize bundle size
    - Implement proper fallback values for unsupported browsers
    - Optimize theme switching performance with CSS transitions
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 8.2 Add comprehensive TypeScript interfaces for theme system


    - Create proper type definitions for all theme configurations
    - Implement type-safe component prop interfaces
    - Add JSDoc documentation for component usage
    - _Requirements: 1.4, 4.1, 4.2_

  - [ ]* 8.3 Implement integration tests for complete theme system
    - Test theme switching across all components and pages
    - Test theme persistence and hydration behavior
    - Test responsive behavior with theme changes
    - _Requirements: 3.1, 3.2, 3.3, 4.1_

- [x] 9. Debug and fix dark mode functionality issues
  - Investigate why dark mode is not properly applying to all components
  - Fix theme detection and application issues
  - Ensure CSS custom properties are correctly applied in dark mode
  - Test theme switching functionality across all pages
  - _Requirements: 3.1, 3.2, 3.3, 3.6_

- [x] 10. Fix header visibility issues
  - Fix market open text visibility by removing excessive opacity
  - Improve notification badge positioning and contrast
  - Ensure proper text visibility in both light and dark themes
  - Clean up unused code and improve component performance
  - _Requirements: 2.1, 2.2, 2.3, 5.1_

- [x] 11. Reposition chart control buttons to prevent content overlap
  - Move Fullscreen and Reset Zoom buttons from bottom-right to top-left position
  - Add CSS to hide built-in TradingView chart controls that may overlap
  - Improve button styling with theme-aware colors and hover effects
  - Add proper functionality to fullscreen and zoom reset buttons
  - Ensure background chart content (prices, values) remains visible
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 12. Fix light mode text visibility and contrast issues
  - Improve text contrast in light mode by updating CSS custom properties
  - Replace hardcoded Tailwind classes with theme-aware CSS custom properties
  - Add explicit light theme selectors to ensure proper theme application
  - Fix sidebar text visibility and button hover states in light mode
  - Ensure all UI elements have proper contrast ratios in both themes
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 5.1_- 
[ ] 13. Fix remaining light mode visibility and contrast issues
  - Investigate and fix any remaining text visibility problems in light mode
  - Ensure proper contrast ratios for all UI elements including sidebar, charts, and data displays
  - Fix any hardcoded colors that aren't responding to theme changes
  - Improve readability of stock data, prices, and chart information in light mode
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 5.1_- [x] 14
. Comprehensive light mode text visibility fixes
  - Fixed all hardcoded Tailwind text colors across all pages (system, settings, portfolio, history)
  - Replaced `text-gray-900 dark:text-white` patterns with `var(--color-text-primary)`
  - Replaced `text-gray-600 dark:text-gray-400` patterns with `var(--color-text-secondary)`
  - Replaced `text-gray-500 dark:text-gray-400` patterns with `var(--color-text-muted)`
  - Updated table headers and content to use theme-aware colors
  - Fixed progress bars and background colors to use CSS custom properties
  - Enhanced chart legend positioning and moved control buttons for better layout
  - Ensured all UI elements have proper contrast ratios in both light and dark modes
  - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 5.1_- 
[x] 15. Comprehensive theme system overhaul and bulletproof text visibility
  - Added aggressive CSS overrides to ensure all text is visible in both themes
  - Enhanced theme application with multiple selector strategies for maximum compatibility
  - Added comprehensive Tailwind class overrides for common text color classes
  - Implemented immediate theme application script in layout to prevent FOUC
  - Added color-scheme CSS property for better browser theme integration
  - Created bulletproof text inheritance system for all HTML elements
  - Enhanced theme toggle with immediate DOM manipulation for instant feedback
  - Added fallback mechanisms for theme detection and application
  - Ensured proper theme persistence and hydration handling
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2_