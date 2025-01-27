import { Toaster } from 'sonner';

export const CustomToaster = () => {
  return (
    <Toaster
      theme="dark"
      className="toaster-theme"
      toastOptions={{
        className: 'bg-black/50 backdrop-blur-md border border-white/10',
        style: {
          background: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: 'white',
        }
      }}
    />
  );
};