import {defineField, defineType} from 'sanity'

export const person = defineType({
  name: 'person',
  title: 'Person',
  type: 'document',
  fields: [
    defineField({
      name: 'handle',
      title: 'Handle',
      type: 'string',
      validation: (Rule) => Rule.required(),
      description: 'DEV handle or name as they signed the comment, e.g. pm25coder.',
    }),
    defineField({
      name: 'url',
      title: 'Profile URL',
      type: 'url',
    }),
    defineField({
      name: 'employer',
      title: 'Employer',
      type: 'string',
      description: 'Only if they named it themselves. Leave empty otherwise.',
    }),
    defineField({
      name: 'outside',
      title: 'Outside this house',
      type: 'boolean',
      initialValue: true,
      description: 'False for Ka\'el / internal audit rows. Do not fold those into the finder count.',
    }),
  ],
  preview: {
    select: {title: 'handle', subtitle: 'employer'},
  },
})
