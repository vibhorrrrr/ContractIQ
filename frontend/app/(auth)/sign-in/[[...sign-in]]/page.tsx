import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="gradient-bg min-h-screen flex items-center justify-center">
      <SignIn
        appearance={{
          elements: {
            rootBox: "mx-auto",
            card: "bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 shadow-2xl",
          },
        }}
      />
    </div>
  );
}
