export interface PasswordValidationResult {
  isValid: boolean;
  score: number; // 0-100
  strength: 'weak' | 'medium' | 'strong';
  errors: string[];
  suggestions: string[];
}

export interface PasswordRequirements {
  minLength: number;
  requireUppercase: boolean;
  requireLowercase: boolean;
  requireNumbers: boolean;
  requireSpecialChars: boolean;
  maxLength?: number;
}

export const DEFAULT_PASSWORD_REQUIREMENTS: PasswordRequirements = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
  maxLength: 128,
};

export const validatePassword = (
  password: string,
  requirements: PasswordRequirements = DEFAULT_PASSWORD_REQUIREMENTS
): PasswordValidationResult => {
  const errors: string[] = [];
  const suggestions: string[] = [];
  let score = 0;

  // Length validation
  if (password.length < requirements.minLength) {
    errors.push(`Password must be at least ${requirements.minLength} characters long`);
    suggestions.push(`Add ${requirements.minLength - password.length} more characters`);
  } else {
    score += 20;
    // Bonus points for longer passwords
    if (password.length >= 12) score += 10;
    if (password.length >= 16) score += 10;
  }

  if (requirements.maxLength && password.length > requirements.maxLength) {
    errors.push(`Password must be no more than ${requirements.maxLength} characters long`);
  }

  // Character type requirements
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumbers = /[0-9]/.test(password);
  const hasSpecialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

  if (requirements.requireUppercase && !hasUppercase) {
    errors.push('Password must contain at least one uppercase letter');
    suggestions.push('Add an uppercase letter (A-Z)');
  } else if (hasUppercase) {
    score += 15;
  }

  if (requirements.requireLowercase && !hasLowercase) {
    errors.push('Password must contain at least one lowercase letter');
    suggestions.push('Add a lowercase letter (a-z)');
  } else if (hasLowercase) {
    score += 15;
  }

  if (requirements.requireNumbers && !hasNumbers) {
    errors.push('Password must contain at least one number');
    suggestions.push('Add a number (0-9)');
  } else if (hasNumbers) {
    score += 15;
  }

  if (requirements.requireSpecialChars && !hasSpecialChars) {
    errors.push('Password must contain at least one special character');
    suggestions.push('Add a special character (!@#$%^&* etc.)');
  } else if (hasSpecialChars) {
    score += 15;
  }

  // Additional security checks
  const hasRepeatedChars = /(.)\1{2,}/.test(password);
  if (hasRepeatedChars) {
    score -= 10;
    suggestions.push('Avoid repeating the same character multiple times');
  }

  const hasSequentialChars = /(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|123|234|345|456|567|678|789|890)/i.test(password);
  if (hasSequentialChars) {
    score -= 10;
    suggestions.push('Avoid using sequential characters (abc, 123, etc.)');
  }

  const hasCommonPatterns = /(?:password|123456|qwerty|admin|user|login)/i.test(password);
  if (hasCommonPatterns) {
    score -= 20;
    suggestions.push('Avoid using common words or patterns');
  }

  // Character diversity bonus
  const uniqueChars = new Set(password.toLowerCase()).size;
  if (uniqueChars >= password.length * 0.7) {
    score += 10;
  }

  // Ensure score is within bounds
  score = Math.max(0, Math.min(100, score));

  // Determine strength
  let strength: 'weak' | 'medium' | 'strong';
  if (score >= 80) {
    strength = 'strong';
  } else if (score >= 60) {
    strength = 'medium';
  } else {
    strength = 'weak';
  }

  const isValid = errors.length === 0;

  return {
    isValid,
    score,
    strength,
    errors,
    suggestions,
  };
};

export const getPasswordStrengthColor = (strength: 'weak' | 'medium' | 'strong'): string => {
  switch (strength) {
    case 'weak':
      return 'text-red-600';
    case 'medium':
      return 'text-yellow-600';
    case 'strong':
      return 'text-green-600';
    default:
      return 'text-gray-400';
  }
};

export const getPasswordStrengthBgColor = (strength: 'weak' | 'medium' | 'strong'): string => {
  switch (strength) {
    case 'weak':
      return 'bg-red-500';
    case 'medium':
      return 'bg-yellow-500';
    case 'strong':
      return 'bg-green-500';
    default:
      return 'bg-gray-300';
  }
};

// Check if password has been compromised (would require API call to haveibeenpwned or similar)
export const checkPasswordBreach = async (password: string): Promise<boolean> => {
  // This is a placeholder for breach checking
  // In a real implementation, you would:
  // 1. Hash the password with SHA-1
  // 2. Send first 5 characters of hash to HaveIBeenPwned API
  // 3. Check if full hash appears in response
  // For now, just return false (not breached)
  return false;
};