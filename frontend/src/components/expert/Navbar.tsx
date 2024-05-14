import React from 'react';
import { Link } from "react-router-dom";
import AuthContext from "../../context/AuthContext1";
import { useContext } from "react";
import { Avatar , Tooltip} from '@mui/material';
import { stringAvatar } from '../../services/expertServices';

const Navbar = () => {
  const userName = localStorage.getItem("userName")
  const authContext = useContext(AuthContext);
  return (
    <div className='flex justify-between items-center shadow-xl bg-white'>
        <div className='flex items-center'>
          <Link to="/expert/dashboard" className='w-14 ml-12 mr-8 py-6'><img src="/assets/logo.png" alt="logo" /></Link>
          <h2 className='text-3xl font-bold text-blue-500'>VORT</h2>
        </div>
        <div className='mr-20 flex items-center'>
            <h2 className='font-bold text-lg text-blue-500 mr-10 cursor-pointer' onClick={authContext?.logoutUser}>Logout</h2>
            <Tooltip title={userName} arrow>
              <Avatar {...stringAvatar(userName ? userName : "")} />
            </Tooltip>
        </div>
    </div>
  )
}

export default Navbar