import React from 'react';
import Nav from '../components/Nav';
import Footer from '../components/Footer';

export default class Layout extends React.Component {
    render() {
        return (
            <div>
               <Nav/>
               <div> {this.props.children} </div>
               <Footer/>
            </div>
        );
    }
}
