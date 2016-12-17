import React from 'react';

export default class DeleteNotification extends React.Component {
    render() { 
        return(
            <div className='notification'>
                <p>The victim has been deleted.</p>
                <div className='btn underline' onClick={ this.props.onUndo }>Undo</div>
                <button type='button' className='close nooutline' onClick={ this.props.onClose }>&times;</button>
            </div>
        );
    }
}

