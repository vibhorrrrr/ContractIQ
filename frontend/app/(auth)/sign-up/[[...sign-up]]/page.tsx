import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="gradient-bg min-h-screen flex items-center justify-center">
      <SignUp
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
