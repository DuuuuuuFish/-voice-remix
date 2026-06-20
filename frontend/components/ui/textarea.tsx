import * as React from "react";

import { cn } from "@/lib/utils";

const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        "min-h-[180px] w-full rounded-[24px] border border-border bg-white/90 px-4 py-3 text-sm text-foreground shadow-sm outline-none transition focus-visible:ring-2 focus-visible:ring-primary/40",
        className,
      )}
      {...props}
    />
  ),
);
Textarea.displayName = "Textarea";

export { Textarea };
