import React from "react";
import PropTypes from "prop-types";
import { Form, Input, Button } from "antd";
import styled from "styled-components";

import floridaManService from "../../services/floridaMan";
import { TeamNumbersContext } from "./TeamNumbers";

const { TextArea } = Input;

const ButtonContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(50px, 1fr));
  grid-gap: 1rem;
`;

const AddNumbersForm = ({ form }) => {
  const [isSubmitting, setIsSubmitting] = React.useState(false);
  const teamNumberContext = React.useContext(TeamNumbersContext);

  const handleAddNumbersInputChange = e => {
    e.preventDefault();
    form.validateFields((err, values) => {
      if (!err) {
        setIsSubmitting(true);
        const numbers = values.numbers.split(",").map(number => number.trim());
        const requests = numbers.map(number =>
          floridaManService.addTeamNumber(number)
        );

        Promise.all(requests)
          .then(responses => {
            form.resetFields();
            setIsSubmitting(false);
            teamNumberContext.setIsAddingNumbers(false);
            teamNumberContext.fetchNumbers();
          })
          .catch(error => {
            setIsSubmitting(false);
            console.error(error);
          });
      }
    });
  };

  return (
    <Form onSubmit={handleAddNumbersInputChange}>
      <Form.Item label="New Team Numbers">
        {form.getFieldDecorator("numbers", {
          rules: [
            { required: true, message: "Please enter at least one number" }
          ]
        })(<TextArea placeholder="Enter numbers here (comma separated)" />)}
      </Form.Item>
      <Form.Item>
        <ButtonContainer>
          <Button
            type="dashed"
            onClick={() => teamNumberContext.setIsAddingNumbers(false)}
          >
            Cancel
          </Button>
          <Button type="primary" htmlType="submit" loading={isSubmitting}>
            Add to Team
          </Button>
        </ButtonContainer>
      </Form.Item>
    </Form>
  );
};

AddNumbersForm.propTypes = {};

export default Form.create({ name: "addTeamNumbers" })(AddNumbersForm);
