'use client';

export function LoadingSkeleton() {
  return (
    <div className="w-full py-2 space-y-4">
      <div className="h-4 w-full rounded-md animate-shimmer"></div>
      <div className="h-4 w-[85%] rounded-md animate-shimmer"></div>
      <div className="h-4 w-[60%] rounded-md animate-shimmer"></div>
    </div>
  );
}
