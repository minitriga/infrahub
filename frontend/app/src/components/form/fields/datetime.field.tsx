import { LabelFormField } from "@/components/form/fields/common";
import { FormAttributeValue, FormFieldProps } from "@/components/form/type";
import { updateFormFieldValue } from "@/components/form/utils/updateFormFieldValue";
import { DatePicker } from "@/components/inputs/date-picker";
import { FormField, FormInput, FormMessage } from "@/components/ui/form";
import { formatISO } from "date-fns";
import { ComponentProps } from "react";

export interface DatetimeFieldProps
  extends FormFieldProps,
    Omit<ComponentProps<typeof DatePicker>, "defaultValue" | "name"> {}

const DatetimeField = ({
  defaultValue,
  description,
  label,
  name,
  rules,
  unique,
  ...props
}: DatetimeFieldProps) => {
  return (
    <FormField
      key={name}
      name={name}
      rules={rules}
      defaultValue={defaultValue}
      render={({ field }) => {
        const fieldData: FormAttributeValue = field.value;

        const handleChange = (newDate: Date) => {
          const newDateValue = formatISO(newDate);
          field.onChange(updateFormFieldValue(newDateValue, defaultValue));
        };

        return (
          <div className="space-y-2">
            <LabelFormField
              label={label}
              unique={unique}
              required={!!rules?.required}
              description={description}
              fieldData={fieldData}
            />

            <FormInput>
              <DatePicker
                {...field}
                date={fieldData?.value ? new Date(fieldData.value as string) : null}
                onChange={handleChange}
                {...props}
              />
            </FormInput>

            <FormMessage />
          </div>
        );
      }}
    />
  );
};

export default DatetimeField;
