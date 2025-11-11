import { Loader2 } from "lucide-react";

export default function Loading() {
  return (
    <div className="h-screen w-full flex items-center justify-center bg-background-light">
      <div className="text-center">
        <Loader2 className="mx-auto animate-spin text-accent mb-4" size={48} />
        <p className="text-lg font-medium text-gray-600">
          Loading Anaya Watchtower...
        </p>
      </div>
    </div>
  );
}
