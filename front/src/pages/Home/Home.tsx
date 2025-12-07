import { Link } from 'react-router-dom';

export const Home: React.FC = () => {
  return (
    <div className="bg-[#00783440] text-[#007834] h-full justify-center items-center space-y-6">
      <div className="flex justify-center items-center h-full w-full gap-6">
        <Link to="/report">
          <button
            className="px-6 py-3 text-sm font-semibold text-white
            bg-primary rounded-xl shadow-lg hover:bg-green-700 transition duration-150
            ease-in-out transform hover:scale-105">
            Zapis wyjaśnień poszkodowanego
          </button>
          </Link>
          <Link to="/statement">
          <button
            className="px-6 py-3 text-sm font-semibold text-white
            bg-primary rounded-xl shadow-lg hover:bg-green-700 transition duration-150
            ease-in-out transform hover:scale-105">
            Zawiadomienie o wypadku
          </button>
        </Link>
      </div>
    </div>
  );
};
