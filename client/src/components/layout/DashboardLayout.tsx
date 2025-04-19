import React from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Home,
  CreditCard,
  Settings,
  Shield,
  User,
  LogOut,
  Menu,
  X,
  Bell,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useIsMobile } from "@/hooks/use-mobile";

interface NavLinkProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  isActive?: boolean;
  onClick?: () => void;
}

function NavLink({ to, icon, label, isActive, onClick }: NavLinkProps) {
  return (
    <Link to={to} onClick={onClick}>
      <div
        className={`flex items-center space-x-3 px-3 py-2 rounded-md transition-colors ${
          isActive
            ? "bg-wallet-primary text-white"
            : "hover:bg-muted"
        }`}
      >
        {React.cloneElement(icon as React.ReactElement, {
          className: "h-5 w-5",
        })}
        <span className="font-medium">{label}</span>
      </div>
    </Link>
  );
}

interface DashboardLayoutProps {
  children: React.ReactNode;
  currentPath: string;
  userName?: string;
  profileImage?: string;
  onLogout?: () => void;
}

export function DashboardLayout({
  children,
  currentPath,
  userName = "User",
  profileImage,
  onLogout,
}: DashboardLayoutProps) {
  const isMobile = useIsMobile();
  const [sidebarOpen, setSidebarOpen] = React.useState(false);

  const navLinks = [
    { to: "/dashboard", icon: <Home />, label: "Dashboard" },
    { to: "/wallet", icon: <CreditCard />, label: "Wallet" },
    { to: "/security", icon: <Shield />, label: "Security" },
    { to: "/profile", icon: <User />, label: "Profile" },
    { to: "/settings", icon: <Settings />, label: "Settings" },
  ];

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  const renderSidebarContent = () => (
    <>
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="bg-wallet-primary text-white p-1.5 rounded-md">
              <CreditCard className="h-5 w-5" />
            </div>
            <h1 className="text-xl font-bold">PVTELV</h1>
          </div>
          {isMobile && (
            <Button variant="ghost" size="icon" onClick={toggleSidebar}>
              <X className="h-5 w-5" />
            </Button>
          )}
        </div>
      </div>

      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-1">
          {navLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              icon={link.icon}
              label={link.label}
              isActive={currentPath === link.to}
              onClick={isMobile ? closeSidebar : undefined}
            />
          ))}
        </div>
      </ScrollArea>

      <div className="p-4 mt-auto">
        <Separator className="mb-4" />
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Avatar className="h-9 w-9">
              <AvatarImage src={profileImage} />
              <AvatarFallback className="bg-wallet-primary/20 text-wallet-primary">
                {userName.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-sm font-medium">{userName}</p>
              <p className="text-xs text-muted-foreground">Account Holder</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onLogout}>
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </>
  );

  return (
    <div className="flex h-screen bg-muted/30">
      {/* Sidebar for desktop */}
      {!isMobile && (
        <aside className="hidden md:flex md:w-64 flex-col border-r bg-background">
          {renderSidebarContent()}
        </aside>
      )}

      {/* Mobile sidebar (off-canvas) */}
      {isMobile && (
        <div
          className={`fixed inset-0 z-50 transform transition-transform duration-300 ease-in-out ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <div className="absolute inset-0 bg-black/50" onClick={closeSidebar} />
          <aside className="relative w-64 h-full flex flex-col bg-background">
            {renderSidebarContent()}
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Mobile header */}
        {isMobile && (
          <header className="h-14 border-b bg-background flex items-center justify-between px-4">
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                <Menu className="h-5 w-5" />
              </Button>
              <h1 className="font-bold flex items-center">
                <span className="bg-wallet-primary text-white p-1 rounded-md mr-2">
                  <CreditCard className="h-4 w-4" />
                </span>
                PVTElA
              </h1>
            </div>
            <Button variant="ghost" size="icon">
              <Bell className="h-5 w-5" />
            </Button>
          </header>
        )}

        {/* Content area */}
        <main className="flex-1 overflow-auto p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
