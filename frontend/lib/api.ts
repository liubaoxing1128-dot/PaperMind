export const API_URL = "https://papermind-production-c6b9.up.railway.app";

export async function chat(question: string) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
    }),
  });

  return await response.json();
}
