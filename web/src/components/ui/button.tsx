import { Button as BaseButton } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";
import { clsx } from "clsx";
import type { ComponentProps } from "react";

const buttonVariants = cva("btn", {
  variants: {
    intent: {
      primary: "btn-primary",
      secondary: "btn-secondary",
      ghost: "btn-ghost",
      social: "btn-social",
    },
    size: {
      md: "btn-md",
      lg: "btn-lg",
    },
  },
  defaultVariants: {
    intent: "primary",
    size: "lg",
  },
});

type ButtonProps = ComponentProps<typeof BaseButton> &
  VariantProps<typeof buttonVariants>;

export function Button({
  className,
  intent,
  size,
  ...props
}: ButtonProps) {
  return (
    <BaseButton
      className={clsx(buttonVariants({ intent, size }), className)}
      {...props}
    />
  );
}
