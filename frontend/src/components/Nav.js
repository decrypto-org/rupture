import React from 'react';
import { IndexLink } from 'react-router';
import Logo from '../img/logo.png';


export default class Nav extends React.Component {
    render() {
        return(
            <div className='navbar navbar-default navbar-fixed-top'>
                <div className='container-fluid'>
                    <div className='navbar-header'>
                        <IndexLink to='/'><img src={ Logo } alt='Dinosaur Egg' title='Go to start page'/></IndexLink>
                    </div>
                </div> 
            </div>
        );
    }
}
