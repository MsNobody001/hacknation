export const isValidEmail = (email: string) => {
  return /\S+@\S+\.\S+/.test(email);
};

export const formatTime = (date: Date) => {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};