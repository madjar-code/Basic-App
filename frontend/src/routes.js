import { useContext } from "react";
import { Route, Navigate } from 'react-router-dom'
import { UserContext } from "./providers/UserContext";
import PropTypes from 'prop-types'


export const NoAuthRoute = (props) => {
  const { user } = useContext(UserContext)

  return (
    <Route
      path={props.path}
      render={(data) =>
        !user ? <props.component {...data}/> : <Navigate to='/'/>
      }
    />
  )
}

NoAuthRoute.propTypes = {
  path: PropTypes.string,
}

export const ProtectedRoute = (props) => {
  const { user } = useContext(UserContext);

  return (
    <Route
      path={props.path}
      render={(data) =>
        user ? <props.component {...data} /> : <Navigate to="/login" />
      }
    />
  );
};

ProtectedRoute.propTypes = {
  path: PropTypes.string,
};