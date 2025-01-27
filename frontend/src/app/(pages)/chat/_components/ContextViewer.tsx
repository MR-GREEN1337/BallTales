"use client"

import React from 'react';
import { Info } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

const ContextViewer = ({ context }: { context: any }) => {
  const formatJSON = (obj: any): JSX.Element => {
    const formatted = JSON.stringify(obj, null, 2);
    const lines = formatted.split('\n');

    return (
      <div className="font-mono">
        {lines.map((line, i) => {
          const indent = line.match(/^\s*/)?.[0].length || 0;
          const content = line.trim();
          
          // Determine if this line contains a key-value pair
          const isKeyValue = content.includes(':');
          const [key, value] = isKeyValue ? content.split(':') : [content, ''];
          
          return (
            <div 
              key={i} 
              className="flex"
              style={{ paddingLeft: `${indent * 8}px` }}
            >
              {isKeyValue ? (
                <>
                  <span className="text-blue-300">{key.replace(/"/g, '')}</span>
                  <span className="text-gray-400">:</span>
                  <span className="text-green-300 ml-2">
                    {value.replace(/[",]/g, '')}
                  </span>
                </>
              ) : (
                <span className="text-gray-300">{content}</span>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="absolute bottom-2 right-2">
      <Dialog>
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <DialogTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="h-3 w-3 p-0 rounded-full bg-white/10 hover:bg-white/20"
                >
                  <Info className="h-3 w-3 text-gray-400" />
                </Button>
              </DialogTrigger>
            </TooltipTrigger>
            <TooltipContent className='bg-black/50 backdrop-blur-md'>
              <p>View how the agent achieved this result</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <DialogContent className="max-w-2xl bg-gray-950 text-white border-gray-800">
          <DialogHeader>
            <DialogTitle className="text-white">Agent Context</DialogTitle>
          </DialogHeader>
          <ScrollArea className="max-h-[60vh] mt-4 rounded-md bg-black/50 p-4">
            {formatJSON(context)}
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ContextViewer;