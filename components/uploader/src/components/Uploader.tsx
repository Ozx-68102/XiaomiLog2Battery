import React from 'react';

import '@uppy/core/css/style.min.css';
import '@uppy/dashboard/css/style.min.css';

type Props = {
  id?: string,
  endpoint?: string,
  setProps?: (props: any) => void,
};

const Uploader: React.FC<Props> = (props) => {
  const { id } = props;
  return (
    <div id={id}>
      <h1>Hello from Uppy 5.0 & TypeScript!</h1>
    </div>
  );
}

export default Uploader;
