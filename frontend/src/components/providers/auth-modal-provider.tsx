"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface AuthModalContextType {
  openAuthModal: () => void;
  closeAuthModal: () => void;
}

const AuthModalContext = createContext<AuthModalContextType | undefined>(undefined);

export function AuthModalProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const { loginWithPopup } = useAuth0();

  const openAuthModal = () => setIsOpen(true);
  const closeAuthModal = () => setIsOpen(false);

  const handleLogin = async (screen_hint?: "signup") => {
    try {
      await loginWithPopup({
        authorizationParams: {
          screen_hint,
        },
      });
      closeAuthModal();
    } catch (error) {
      console.error("Popup login failed", error);
    }
  };

  return (
    <AuthModalContext.Provider value={{ openAuthModal, closeAuthModal }}>
      {children}
      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Sign in to Reverie</DialogTitle>
            <DialogDescription>
              You need an account to track your environmental impact and save your upcycling projects.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-4 py-4">
            <Button onClick={() => handleLogin()} className="w-full">
              Log In
            </Button>
            <Button
              variant="outline"
              onClick={() => handleLogin("signup")}
              className="w-full"
            >
              Create Account
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </AuthModalContext.Provider>
  );
}

export function useAuthModal() {
  const context = useContext(AuthModalContext);
  if (context === undefined) {
    throw new Error("useAuthModal must be used within an AuthModalProvider");
  }
  return context;
}
