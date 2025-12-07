import { Route, Routes } from 'react-router-dom';

import { VictimExplanationForm } from '@/pages';
import { Message } from '@/types';
import { ChatWidget } from './ChatWidget';
import { useCtx } from '@/context';
import { UserCog } from 'lucide-react';
import { Link } from 'react-router-dom';
import { AnalyzeForm } from '@/pages/AnalyzeForm';

const App = () => {
  const ctx = useCtx();
  const chatHistory: Message[] = [];

  return (
    <>
      <div className="flex justify-between px-8">
        <Link to="/" >
          <img src="/logo_zus_darker_with_text.svg" alt="zus logo" className="block h-10 p-2"  />
        </Link>
        <Link to="/analyze" className="flex flex-col justify-center text-[#007834]">
            <UserCog size={25} />
        </Link>
      </div>
      <div className="grid grid-cols-3 bg-[#00783440] text-[#007834] h-[calc(100vh-40px)]">
        <div className="col-span-2 margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto">
          <Routes>
            <Route path="/" element={<VictimExplanationForm />} />
            <Route path="/analyze" element={<AnalyzeForm />} />
          </Routes>
        </div>
        <div className="margin-1 m-3 rounded-xl bg-neutral-100 max-h-full overflow-auto relative">
          <ChatWidget
            initialMessages={chatHistory}
            onCollectedData={collectedData => ctx.setCollectedData(collectedData)}
          />
        </div>
      </div>
    </>
  );
};

export { App };
