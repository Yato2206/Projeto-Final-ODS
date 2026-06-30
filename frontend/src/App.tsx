import React from "react";
import {createRoot} from "react-dom/client";
import {createBrowserRouter, RouterProvider} from "react-router";
import {SearchBar} from "./components/SearchBar";
import {Home} from "./components/Home";
import {DashboardScreen} from "./components/Dashboard";

const router = createBrowserRouter([
    {
        path:"/",
        element: <Home/>,
        children: [
            {
                path:"/dashboard",
                element: <DashboardScreen/>
            },
            {
                path:"/documents",
                element: <SearchBar/>
            }
        ]
    },
]);

createRoot(document.getElementById("container")!).render(
    <RouterProvider router={router} />
);