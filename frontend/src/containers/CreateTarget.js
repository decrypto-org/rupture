import React from 'react';
import { ModalHeader, ModalTitle, ModalClose, ModalBody, ModalFooter } from 'react-modal-bootstrap';
import { Form } from 'react-bootstrap';
import axios from 'axios';

export default class CreateTarget extends React.Component {


    handleSubmit = (event) => {
        let method;
        if (this.refs.method1.checked) {
            method = parseInt(this.refs.method1.value, 10);
        }
        else {
            method = parseInt(this.refs.method2.value, 10);
        }
        event.preventDefault();
        axios.post('/breach/target', {
            name: this.refs.name.value,
            endpoint: this.refs.url.value,
            prefix: this.refs.prefix.value,
            alphabet: this.refs.secral.value,
            secretlength: this.refs.length.value,
            alignmentalphabet: this.refs.alignal.value,
            recordscardinality: this.refs.card.value,
            method: method 
        })
        .then(res => {
            let target_name = res.data.target_name;
            console.log(res);
            this.props.onUpdate(target_name);
        })
        .catch(error => {
            console.log(error);
        });
    }

    render() {
        return(
            <div>
                <ModalHeader>
                    <ModalClose type='button' className='btn btn-default' onClick={ this.props.onClose }>Close</ModalClose>
                    <ModalTitle> Create Target </ModalTitle>
                </ModalHeader>

                <ModalBody>
                    <div className='row'>
                        <div className='col-xs-offset-1 col-xs-11'>
                            <Form onSubmit={ this.handleSubmit }>
                                <div className='form-group'>
                                    <label htmlFor='name' className='col-xs-5 progressmargin'>Name:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='text' className='form-control' ref='name'/>
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='url' className='col-xs-5 progressmargin'>Endpoint url:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='url' className='form-control' ref='url'/>
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='prefix' className='col-xs-5 progressmargin'>Known prefix:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='text' className='form-control' ref='prefix'/>
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='length' className='col-xs-5 progressmargin'>Secret length:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='number' className='form-control' ref='length'/>
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='secral' className='col-xs-5 progressmargin'>Secret Alphabet:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='text' className='form-control' ref='secral'/>
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='alignal' className='col-xs-5 progressmargin'>Alignment Alphabet:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='text' className='form-control' placeholder='abcdefghijklmnopqrstuvwxyz' 
                                            ref='alignal' />
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='card' className='col-xs-5 progressmargin'>Record cardinality:</label>
                                    <div className='col-xs-6 progressmargin'>
                                        <input type='number' className='form-control' defaultValue='1'  ref='card'/>
                                    </div>
                                </div>
                                <div className='form-group'>
                                    <label htmlFor='methods' className='col-xs-5 progressmargin'>Method:</label>
                                    <div className='radio' name='methods'>
                                        <label className='col-xs-4 serialmargin'>
                                            <input type='radio' name='method' ref='method1' value='1' defaultChecked/>Serial
                                        </label>
                                    </div>
                                    <div className='col-xs-5'></div>
                                    <div className='radio'>
                                        <label className='col-xs-4 dividemargin'>
                                            <input type='radio' name='method' ref='method2' value='2' />Divide &amp; Conquer
                                        </label>
                                    </div>
                                </div>
                            </Form>
                        </div>
                    </div>
                </ModalBody>

                <ModalFooter>
                    <input type='submit' className='btn btn-default' value='Submit'
                        onClick={ (event) =>  { this.handleSubmit(event); this.props.onClose(); }}>
                    </input>
                </ModalFooter>
            </div>
        );
    }
}
