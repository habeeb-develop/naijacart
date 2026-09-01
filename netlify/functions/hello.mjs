export default async () => {
  return new Response(
    JSON.stringify({
      message: "NaijaCart Netlify backend is working!"
    }),
    {
      headers: {
        "Content-Type": "application/json"
      }
    }
  );
};