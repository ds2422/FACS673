export const withBackoff = async <T,>(
  fn: () => Promise<T>,
  maxRetries: number = 5
): Promise<T> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) {
        console.error("Max retries reached. Failing.", error);
        throw error;
      }
      const delay = Math.pow(2, i) * 1000 + Math.random() * 1000;
      console.log(`Retrying in ${delay}ms...`);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw new Error("Failed after maximum retries.");
};