import { Route, Routes } from 'react-router-dom';

import { VictimExplanationForm } from '@/pages';
import { Message } from '@/types';
import { ChatWidget } from './ChatWidget';
import { useCtx } from '@/context';

const App = () => {
  const ctx = useCtx();
  const chatHistory: Message[] = [];

  return (
    <>
      <div className="grid grid-cols-3 bg-[#00783440] text-[#007834] h-[100vh]">
        <div className="col-span-2 margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto">
          <Routes>
            <Route path="/" element={<VictimExplanationForm />} />
          </Routes>
        </div>
        <div className="margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto relative">
          <ChatWidget initialMessages={chatHistory} onCollectedData={collectedData => ctx.setCollectedData(collectedData)} />
        </div>
      </div>
    </>
  );
};

export { App };
