import React from "react";
import {createRoot} from "react-dom/client";
import {createBrowserRouter, RouterProvider} from "react-router";
import {SearchBar} from "./components/SearchBar";
//import {SearchResults} from "./components/SearchResults";

const router = createBrowserRouter([
    {
        path:"/",
        element: <SearchBar/>,
        /*children:[
            {
                path:"results",
                element: <SearchResults/>
            }
        ]*/
    }
]);

createRoot(document.getElementById("container")!).render(
    <RouterProvider router={router} />
);