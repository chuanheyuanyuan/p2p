export const maskPhone = (phone?: string) => {
  if (!phone) return '-';
  const digits = phone.replace(/\D/g, '');
  if (digits.length <= 4) return phone;
  const prefix = phone.trim().startsWith('+') ? '+' : '';
  const masked = `${digits.slice(0, 3)}${'*'.repeat(Math.max(1, digits.length - 5))}${digits.slice(-2)}`;
  return `${prefix}${masked}`;
};

export const formatCurrency = (value: number, currency = '₵') =>
  `${currency}${Number(value ?? 0).toLocaleString(undefined, { minimumFractionDigits: 0 })}`;
