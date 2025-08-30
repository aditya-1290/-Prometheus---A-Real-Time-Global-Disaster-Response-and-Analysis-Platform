import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import DisasterDetails from '../pages/DisasterDetails';
import ResourceManagement from '../pages/ResourceManagement';
import Layout from '../components/Layout';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: '/',
        element: <Dashboard />,
      },
      {
        path: '/disaster/:id',
        element: <DisasterDetails />,
      },
      {
        path: '/resources',
        element: <ResourceManagement />,
      },
    ],
  },
]);

const AppRouter = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter;
